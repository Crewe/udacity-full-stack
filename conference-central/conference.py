#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'


from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import BooleanMessage
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import QueryForm
from models import QueryForms
from models import TeeShirtSize
from models import StringMessage
from models import Session
from models import SessionForm, SessionForms
from models import TypeOfSession

from utils import getUserId

from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
MEMCACHE_SPEAKER_KEY = "_FEATURED_SPEAKER"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": ["Default", "Topic"]
}

OPERATORS = {'EQ': '=',
             'GT': '>',
             'GTEQ': '>=',
             'LT': '<',
             'LTEQ': '<=',
             'NE': '!='
             }

FIELDS = {'CITY': 'city',
          'TOPIC': 'topics',
          'MONTH': 'month',
          'MAX_ATTENDEES': 'maxAttendees',
          'DURATION': 'duration',
          'SESS_START_TIME': 'startTime',
          'TYPE_OF_SESSION': 'typeOfSession'
          }

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)

SESS_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

SESS_POST_REQUEST = endpoints.ResourceContainer(
    SessionForm,
    websafeConferenceKey=messages.StringField(1),
)

SESS_TYPE_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    typeOfSession=messages.StringField(2)
)

SESS_WISH_POST_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeSessionKey=messages.StringField(1)
)

SESS_FILTER_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    operator=messages.StringField(2),
    value=messages.StringField(3)
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='conference', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""

# - - - Conference objects - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf


    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # Ensure a profile gets created or conference retreival will fail.
        profile = self._getProfileFromUser()
        if not profile:
            raise endpoints.ConflictException("Unable to create or retrieve profile.")
        if not request.name:
            raise endpoints.BadRequestException("Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeKey']
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference, send email to organizer confirming
        # creation of Conference & return (modified) ConferenceForm
        Conference(**data).put()
        taskqueue.add(params={'email': user.email(),
                              'conferenceInfo': repr(request)},
                      url='/tasks/send_confirmation_email')

        return request


    @ndb.transactional()
    def _updateConferenceObject(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        # update existing conference
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(ConferenceForm, ConferenceForm,
                      path='conference',
                      http_method='POST', name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)


    @endpoints.method(CONF_POST_REQUEST, ConferenceForm,
                      path='conference/{websafeConferenceKey}',
                      http_method='PUT', name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)


    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
                      path='conference/{websafeConferenceKey}',
                      http_method='GET', name='getConference')
    def getConference(self, request):
        """Return requested conference (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='getConferencesCreated',
                      http_method='POST',
                      name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, getattr(prof, 'displayName'))
                   for conf in confs]
        )


    def _getSessionQuery(self, request, ancestor=None):
        """Return formatted query from the submitted filter"""
        if not ancestor:
            q = Session.query()
        else:
            a_key = ancestor
            q = Session.query(ancestor=ndb.Key(urlsafe=a_key))

        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Session.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Session.name)

        for filtr in filters:
            if filtr["field"] in ["duration"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q


    def _getConferenceQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)
        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q


    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) for field in f.all_fields()}
            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)


    @endpoints.method(QueryForms, ConferenceForms,
                      path='queryConferences',
                      http_method='POST',
                      name='queryConferences')
    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._getConferenceQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizerUserId)) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(items=[
            self._copyConferenceToForm(conf, names[conf.organizerUserId])
            for conf in conferences]
        )


# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf


    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                displayName=user.nickname(),
                mainEmail=user.email(),
                teeShirtSize=str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()

        return profile      # return Profile


    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
            prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)


    @endpoints.method(message_types.VoidMessage, ProfileForm,
                      path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()


    @endpoints.method(ProfileMiniForm, ProfileForm,
                      path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)


# - - - Registration - - - - - - - - - - - - - - - - - - - -

    @ndb.transactional(xg=True)
    def _conferenceRegistration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsck)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsck)
                # remove sessions from wishlist
                seshs = Session.query(ancestor=ndb.Key(urlsafe=wsck))                
                for session in seshs:
                    s_key = session.key.urlsafe()
                    if s_key in prof.sessionWishlist:
                        prof.sessionWishlist.remove(s_key)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='conferences/attending',
                      http_method='GET', name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser()  # get user Profile
        conf_keys = [ndb.Key(urlsafe=wsck) for wsck in prof.conferenceKeysToAttend]
        conferences = ndb.get_multi(conf_keys)

        # get organizers
        organisers = [ndb.Key(Profile, conf.organizerUserId) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[
            self._copyConferenceToForm(conf, names[conf.organizerUserId])
            for conf in conferences]
        )


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/{websafeConferenceKey}',
                      http_method='POST', name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request)


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='conference/{websafeConferenceKey}',
                      http_method='DELETE', name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Unregister user for selected conference."""
        return self._conferenceRegistration(request, reg=False)


# - - - Featured Speaker - - - - - - - - - - - - - - - - - - - -

    def _getMemcacheData(self, conference, sessions):
        """Format the featured speaker message to say what 
        sessions the speaker is speaking at and generate a 
        conference-specific memcache key for the featured speaker.
        """
        sessionNames = ""
        for session in sessions:
            sessionNames += session.name + ", "

        sessionNames = sessionNames[:len(sessionNames) - 2]
        sessionNames = sessionNames[::-1]
        sessionNames = sessionNames.replace(" ,", " dna ,", 1)
        sessionNames = sessionNames[::-1]
        speakingAt = "{0} is speaking at: {1}".format(session.speaker, sessionNames)
        memcacheKey = conference.name.replace(" ", "_").upper()
        memcacheKey += MEMCACHE_SPEAKER_KEY
        return memcacheKey, speakingAt


    @staticmethod
    def _setSpeakerInMemcache(memcacheKey, message):
        """Add a featured speaker key to the memcache. The most recent
        speaker with multiple session will be in the cache.
        """
        memcache.set(memcacheKey, message)


    @endpoints.method(CONF_GET_REQUEST, StringMessage,
                      path='conference/featuredSpeaker/get',
                      http_method='GET',
                      name='getFeaturedSpeaker')
    def getFeaturedSpeaker(self, request):
        """Return featured speaker from memcache."""
        wsck = request.websafeConferenceKey
        if not wsck:
            raise endpoints.BadRequestException(
                "You must specify a conference key.")
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException("No conference found with that key.")
        confNameKey = conf.name.upper().replace(" ", "_")
        keySpeaker = memcache.get(confNameKey + MEMCACHE_SPEAKER_KEY)
        if not keySpeaker:
            keySpeaker = ""
        return StringMessage(message=keySpeaker)

# - - - Announcements - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by memcache cron
        job & putAnnouncement().
        """
        confs = Conference.query(ndb.AND(
                                 Conference.seatsAvailable <= 5,
                                 Conference.seatsAvailable > 0)
                                 ).fetch(projection=[Conference.name])

        if confs:
            # If there are almost sold out conferecnes, format announcement
            # and set it in the memecache
            announcement = '{0} {1}'.\
                format('Last chance to attend! The following conferecences '
                       'are nearly sold out:',
                       ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences, delete the memcache
            # announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

        return announcement

    @endpoints.method(message_types.VoidMessage, StringMessage,
                      path='conference/announcement/get',
                      http_method='GET',
                      name='getAnnouncement')
    def getAnnouncement(self, request):
        """Return Announcement from memcache."""
        announcement = memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY)
        if not announcement:
            announcement = ""
        return StringMessage(message=announcement)


# - - - Sessions - - - - - - - - - - - - - - - - - - - -

    def _copySessionToForm(self, sess):
        """Copy fieleds from the Session to the SessionForm."""
        sf = SessionForm()
        for field in sf.all_fields():
            if hasattr(sess, field.name):
                if field.name == 'typeOfSession':
                    setattr(sf, field.name,
                            getattr(TypeOfSession, getattr(sess, field.name)))
                elif field.name in ('startTime', 'date'):
                    setattr(sf, field.name, str(getattr(sess, field.name)))
                else:
                    setattr(sf, field.name, getattr(sess, field.name))
            elif field.name == 'websafeKey':
                setattr(sf, field.name, sess.key.urlsafe())

        sf.check_initialized()
        return sf


    def _createSession(self, request):
        """Create a session in a conference."""
        # preload necessary data items
        wsck = request.websafeConferenceKey
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        conf = ndb.Key(urlsafe=wsck).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can add a session to the conference.')

        if not request.name:
            raise endpoints.BadRequestException("Session 'name' field required")

        # Check that session names are unique to a conference
        sameNameQuery = Session.query(ancestor=ndb.Key(urlsafe=wsck)).\
            filter(Session.name != "TBA").\
            filter(Session.name == request.name)
        if sameNameQuery.count() > 0:
            raise endpoints.BadRequestException(
                "A session already exists with that name for this conference.")

        # generate Session Key based on conference key,
        # session id, and session name.
        c_key = ndb.Key(urlsafe=request.websafeConferenceKey)
        s_id = Session.allocate_ids(size=1, parent=c_key)[0]
        s_key = ndb.Key(Session, s_id, parent=c_key)

        session = Session(key=s_key)

        for field in request.all_fields():
            data = getattr(request, field.name)
            if data not in (None, []):
                if field.name == 'startTime':
                    data = datetime.strptime(data, "%H:%M:%S").time()
                if field.name == 'date':
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                if field.name == 'typeOfSession':
                    data = str(data)

                setattr(session, field.name, data)

        session.put()

        # Check te see if the speaker of the sessions is doing any
        # other sessions. If so make them a featured speaker in memcache
        spkrSessions = Session.query(ancestor=ndb.Key(urlsafe=wsck)).\
            filter(Session.speaker == session.speaker)
        if spkrSessions.count() > 1:
            memcacheKey, message = self._getMemcacheData(conf, spkrSessions)
            taskqueue.add(params={'memcacheKey': memcacheKey,
                                  'message': message},
                          url='/tasks/set_featured_speaker')
        return self._copySessionToForm(session)


    @endpoints.method(SESS_POST_REQUEST, SessionForm,
                      path='session/{websafeConferenceKey}',
                      http_method='POST',
                      name='createSession')
    def createSession(self, request):
        """Create new session in a conference."""
        return self._createSession(request)


    @endpoints.method(SESS_GET_REQUEST, SessionForms,
                      path='session/{websafeConferenceKey}',
                      http_method='GET',
                      name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return sessions that are in a conference."""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        sessions = Session.query(ancestor=ndb.Key(urlsafe=request.websafeConferenceKey))
        return SessionForms(
            sessions=[self._copySessionToForm(sesh) for sesh in sessions]
        )


    @endpoints.method(SESS_TYPE_GET_REQUEST, SessionForms,
                      path='session/type/{websafeConferenceKey}',
                      http_method='GET',
                      name='getSessionsByType')
    def getSessionsByType(self, request):
        """Return sessions in a conference of a certain type."""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # Filter sessions on their conference key and the type of session
        sessions = Session.query(
            ancestor=ndb.Key(urlsafe=request.websafeConferenceKey)
        ).filter(Session.typeOfSession == request.typeOfSession)
        return SessionForms(
            sessions=[self._copySessionToForm(sesh) for sesh in sessions]
        )


    @endpoints.method(StringMessage, SessionForms,
                      path='session/speaker',
                      http_method='GET',
                      name='getSessionsBySpeaker')
    def getSessionsBySpeaker(self, request):
        """Get sessions by a speaker accross all conferences."""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # Filter sessions on speaker name
        sessions = Session.query().filter(Session.speaker == request.message)
        return SessionForms(
            sessions=[self._copySessionToForm(sesh) for sesh in sessions]
        )


    @endpoints.method(SESS_WISH_POST_REQUEST, BooleanMessage,
                      path='profile/wishlist/{websafeSessionKey}',
                      http_method='POST',
                      name='addSessionToWishlist')
    def addSessionToWishlist(self, request):
        """Add a sessions to a profiles wish to attend wishlist."""
        retval = False
        wssk = request.websafeSessionKey
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # Get the session
        session = ndb.Key(urlsafe=wssk).get()
        if not session:
            raise endpoints.NotFoundException(
                'No session found with key: {}'.format(wssk))

        # Get the profile
        user_id = getUserId(user)
        profile = ndb.Key(Profile, user_id).get()

        # Check that it's not already on the wishlist
        if wssk in profile.sessionWishlist:
            raise ConflictException("This session is already in your wishlist.")

        # Check that the session is in a conference the user is registered in
        if profile.conferenceKeysToAttend:
            seshs = [Session.query(ancestor=ndb.Key(urlsafe=p_key))
                     for p_key in profile.conferenceKeysToAttend]
            if not seshs:
                raise endpoints.ForbiddenException(
                    "You are not attending the conference that this session is in.")
            profile.sessionWishlist.append(wssk)
            profile.put()
            retval = True
        else:
            raise endpoints.ForbiddenException(
                "You are not attending the conference that this session is in.")

        return BooleanMessage(data=retval)


    @endpoints.method(CONF_GET_REQUEST, SessionForms,
                      path='profile/wishlist/{websafeConferenceKey}',
                      http_method='GET',
                      name='getSessionsInWishlist')
    def getSessionsInWishlist(self, request):
        """Get the sessions that are in the users wishlist, for the given conference key."""
        wsck = request.websafeConferenceKey
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # Get the profile
        user_id = getUserId(user)
        profile = ndb.Key(Profile, user_id).get()
        sessions = [ndb.Key(urlsafe=wssk).get() for wssk in profile.sessionWishlist]

        # If the session's parent key doesn't match the conference key
        # remove it from the list of sessions to display.
        for session in sessions:
            if session.key.parent().urlsafe() != wsck:
                sessions.remove(session)

        return SessionForms(
            sessions=[self._copySessionToForm(sesh) for sesh in sessions]
        )


    @endpoints.method(SESS_WISH_POST_REQUEST, BooleanMessage,
                      path='profile/wishlist/{websafeSessionKey}',
                      http_method='DELETE',
                      name='deleteSessionInWishlist')
    def deleteSessionInWishlist(self, request):
        """Delete a session from the user's wishlist."""
        wssk = request.websafeSessionKey
        retval = False

        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # Get the user profile and remove the session if it's there
        user_id = getUserId(user)
        profile = ndb.Key(Profile, user_id).get()
        if wssk in profile.sessionWishlist:
            profile.sessionWishlist.remove(wssk)
            retval = True

        # Update the profile
        profile.put()
        return BooleanMessage(data=retval)


    @endpoints.method(SESS_FILTER_GET_REQUEST, SessionForms,
                      path='session/duration/{websafeConferenceKey}',
                      http_method='GET',
                      name='getSessionsByDuration')
    def getSessionsByDuration(self, request):
        """Filter sessions based on its duration in a conference."""
        # Authorize
        wsck = request.websafeConferenceKey
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # Fill the query to have field, op and value
        query = QueryForm(field='DURATION',
                          operator=request.operator,
                          value=request.value)
        sessions = self._getSessionQuery(
            QueryForms(filters=[query]), ancestor=wsck)
        return SessionForms(
            sessions=[self._copySessionToForm(session) for session in sessions]
        )


    @endpoints.method(QueryForms, SessionForms,
                      path='querySessions',
                      http_method='POST',
                      name='querySessions')
    def querySessions(self, request):
        """Filter sessions based on its type and start time."""
        # Authorize
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # check for the first start time inequality and pull it out,
        # otherwise business as usual.
        typeToRemove = None
        fltrd_sess = []
        for queryform in request.filters:
            if queryform.field == "SESS_START_TIME":
                typeToRemove = queryform
                request.filters.remove(queryform)

        sessions = self._getSessionQuery(request)

        # Manually remove the sessions of a particular type
        if typeToRemove:
            for sesh in sessions:
                op = None
                try:
                    op = OPERATORS[typeToRemove.operator]
                    op = typeToRemove.operator
                except KeyError:
                    raise endpoints.BadRequestException(
                        "Filter contains invalid field or operator.")

                if sesh.startTime:
                    try:
                        filter_time = datetime.strptime(typeToRemove.value, "%H:%M:%S").time()
                    except:
                        raise endpoints.BadRequestException("Incorrect time format. Expecting: HH:MM:SS")
                    if op == "EQ":
                        if sesh.startTime == filter_time:
                            fltrd_sess.append(sesh)
                    elif op == "GT":
                        if sesh.startTime > filter_time:
                            fltrd_sess.append(sesh)
                    elif op == 'GTEQ':
                        if sesh.startTime >= filter_time:
                            fltrd_sess.append(sesh)
                    elif op == 'LT':
                        if sesh.startTime < filter_time:
                            fltrd_sess.append(sesh)
                    elif op == 'LTEQ':
                        if sesh.startTime <= filter_time:
                            fltrd_sess.append(sesh)
                    elif op == 'NE':
                        if sesh.startTime != filter_time:
                            fltrd_sess.append(sesh)

            # Return time filtered sessions
            return SessionForms(
                sessions=[self._copySessionToForm(session) for session in fltrd_sess]
            )

        # Return sessions if query was standard
        return SessionForms(
            sessions=[self._copySessionToForm(session) for session in sessions]
        )


api = endpoints.api_server([ConferenceApi])  # register API
