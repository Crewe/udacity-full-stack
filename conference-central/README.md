# Conference Central (ud858)

This project is to develop a API server to support the [Conference Central][7] 
conference organization app that exists on the web using Python. The API supports
the following functionality found within the app: user authentication, user 
profiles, conference information, and various manners in which to query the data.
The full conference API can be accessed via Google's [API Explorer][8].

# Technologies Used and Setup
### Products
- [App Engine][1]

### Language
- [Python][2]

### APIs
- [Google Cloud Endpoints][3]

### Setup Instructions
1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance of this sample.
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][4].
1. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
1. (Optional) Mark the configuration files as unchanged as follows:
   `$ git update-index --assume-unchanged app.yaml settings.py static/js/app.js`
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting your local server's address (by default [localhost:8080][5].)
1. (Optional) Generate your client library(ies) with [the endpoints tool][6].
1. Deploy your application.


# Tasks and Query Problem
## Task 1
**What where your design choices for session and speaker implementation?
Explain in a couple of papragraphs your design choices for session and speaker 
implementation.**

My design incorporated sessions as a child of a conference. This made it easier
to retrieve sessions of a conference by just having a conference key.  For the 
speaker I opted to simply have the speaker as a string in the session, this was
because looking up sessions by speaker is not an overly complex task.  However,
the downside is that if the speaker name needed correcting, then you would have
to fix every sessions individually which could be quite cumbersome, as there's
no guaruntee that they were all mispelled the same way.

Also, sessions may only be added to a wishlist if the user is attending the 
conference it's in. And if you unregister from the conference the sessions 
associated with that conference will also be removed from the wishlist.

## Task 3
**Think about other types of queries that would be useful for this application.
Describe the purpose of 2 new queries and write the code that would perform them.**

Two additional queries that would come in handy would be querying sessions of a
conference by it's duration and the ability to query sessions by it's type.
There may be cases were an attendee may wish to attend as many sessions as
possible and so will seek out shorter ones.  The attendee may also only be
interested in sessions of a partiuclar type, such as a workshop, because they
find hands-on learning more effective for them.

As such, the `getSessionsByDuration()` endpoint was implemented.  Taking a
conference key, duration (in minutes), and operator `EQ`, `LT`, etc. much like
the conference query endpoint.  It will find sessions of a conference that are
equal to (EQ), longer than (GT), or any other inequality of the session's
duration and return a list of qualifiying sessions.

Also there is the `getSessionsByType()` endpoint. Returning a list of sessions
that are of a particular type: `WORKSHOP`, `LECTURE`, `KEYNOTE`, or
`NOT_SPECIFIED` for a given conference key.  If the type is not found, nothing
is returned.

##### Valid Query Operators

|Operator | Equivalent
----------|-----------
`EQ` | `=`
`GT` | `>`
`GTEQ` | `>=`
`LT`| `<`
`LTEQ` | `<=`
`NE` | `!=`

##### Valid Field Properties For Confernce Queries
|Field | Kind.Property
-------|--------------
`CITY` | `Conference.city`
`TOPIC` | `Conference.topics`
`MONTH` | `Conference.month`
`MAX_ATTENDEES` | `Conference.maxAttendees`
`DURATION` | `Conference.duration`

##### Valid Field Properties For Session Queries
|Field | Kind.Property
-------|--------------
`SESS_START_TIME` | `Session.startTime`
`TYPE_OF_SESSION` | `Session.typeOfSession`

##### Valid Session Types:
`WORKSHOP`, `LECTURE`, `KEYNOTE`, and `NOT_SPECIFIED` is the default for 
sessions when not specified at creation.

#### Solve the following query related problem:

**Let’s say that you don't like workshops and you don't like sessions after 7 pm.
How would you handle a query for all non-workshop sessions before 7 pm? What is
the problem for implementing this query? What ways to solve it did you think of?**

The problem would be the inequality filter on the session start time, and
filtering out non-workshops, as you can only perform an inequality query on one
property per query. One way around this would be obtaining the keys of all
non-workshop entities, then performing an inequality query on the start time and
displaying those results.

This is handled in the `querySessions()` endpoint. It queries all sessions much
like `queryConferences` but has also been expanded to
allow for querying of sessions using multiple filters. Enabling the ablitiy to 
query sessions between a particular time of day.


[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool
[7]: https://und-crewe-0001.appspot.com/
[8]: https://und-crewe-0001.appspot.com/_ah/api/explorer