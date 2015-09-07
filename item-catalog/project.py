# project.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify, make_response, Markup, escape
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import random
import string
import datetime
import PyRSS2Gen

APPLICATION_NAME = "Item Catalog Application"
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
HOST = "http://localhost:8000"

app = Flask(__name__)
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# RSS feed for items
@app.route('/catalog/rss.xml')
def catalogRSS():
    """Generates an RSS2.0 Feed for items in the catalog.

    This could go two was, but I wan unsure about what would
    perform better. 

    A) Generating the RSS feed on the fly everytime you hit the
       endpoint. Although I couldn't imagine it being much worse
       than JSON, but it would if the file was sufficiently large.
    B) Generate a file in the root after a new item is added to the
       database, and then serve it via file read. Which I feel is
       better of the two.

    Currenly using A becasue folder/file permissions may affect people.
    It's also easier :P
    """

    rss = generateRSS()
    #with open("rss.xml", "r") as rss_file:
    #    rss_feed = rss_file.read()
    response = make_response(rss.to_xml(), 200)
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


# Some basic API JSON endpoints
@app.route('/catalog.json')
def catalogJSON():
    categories = getCategories()
    items = getAllItems()
    data = set()

    Catalog = [c.serialize for c in categories]
    for cat in Catalog:
        for item in items:
            if item.category.name == cat['name']:
                cat['items'] = item.serialize
                data
        print data

    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/items.json')
def itemsJSON():
    items = getAllItems()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/categories.json')
def categoriesJSON():
    categories = getCategories()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', state=login_session['state'])


@app.route('/catalog/gconnect', methods=['POST'])
def googleConnect():
      # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/catalog/disconnect')
def disconnect():
    # Reset the user's sesson.
    print login_session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You have been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You weren't even logged in.")
        return redirect(url_for('showCatalog'))


def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
def showCatalog():
    # Show 6 most recent items
    categories = getCategories()
    items = getAllItems()
    # Reverse the list so the most recent items are at the front
    items = items[::-1]
    return render_template('index.html', 
                           categories=categories, 
                           recent_items=items[:6])


@app.route('/catalog/<cat_name>/items')
def showCategory(cat_name):
    # Show the items within a category
    category = getCategory(cat_name)
    if not category:
        return redirect('NotFound')

    items = getItems(cat_name)
    categories = getCategories()
    return render_template('category.html',
                           categories=categories,
                           category=cat_name, 
                           items=items)


@app.route('/catalog/<cat_name>/<item_name>/details')
def showItem(cat_name, item_name):
    # Show the detalis about an item
    item = getItem(item_name)
    if not item:
        return redirect('NotFound')

    creator = getUserInfo(item.user_id)
    return render_template('item.html', item=item, creator=creator)


@app.route('/catalog/<cat_name>/item/add', methods=['GET', 'POST'])
def addItem(cat_name):
    if 'username' not in login_session:
        return redirect('/catalog/login')
    category = getCategory(cat_name)
    categories = getCategories()
    if not category:
        return redirect('NotFound')
    if request.method == 'POST':
        try:
            # Keep things clean looking by always having some sort of image
            if request.form['item-pic']:
                picture_url = request.form['item-pic']
            else:
                picture_url = 'http://placehold.it/173x195'
            if request.form['item-thumb']:
                thumbnail_url = request.form['item-thumb'] 
            else:
                thumbnail_url = 'http://placehold.it/320x150'

            picture_url = 'http://placehold.it/173x195'
            newItem = Item(user_id=login_session['user_id'],
                           name=escape(request.form['item-name']),
                           price=escape(request.form['item-price']),
                           thumbnail=escape(thumbnail_url),
                           picture=escape(picture_url),
                           category_id=request.form['item-cat'],
                           description=escape(request.form['item-desc']))
            session.add(newItem)
            session.commit()
            # Update the RSS Feed: SEE catalogRSS()
            #generateRSS()
            flash("Successfully added {0} to {1}!".format(newItem.name, category.name))
            return redirect(url_for('showCategory', cat_name=category.name))
        except:
            flash("Unable to add item to {0} category".format(category.name), 'error')
            return redirect(url_for('showCategory', cat_name=category.name))
    else:
        return render_template('additem.html', category=category, categories=categories)


@app.route('/catalog/<cat_name>/<item_name>/edit', methods=['GET', 'POST'])
def editItem(cat_name, item_name):
    if 'username' not in login_session:
        return redirect('/catalog/login')
    itemToEdit = getItem(item_name)
    if request.method == 'POST':
        if request.form['item-name']:
            itemToEdit.name = escape(request.form['item-name'])
        if request.form['item-price']:
            itemToEdit.price = escape(request.form['item-price'])
        if request.form['item-thumb']:
            itemToEdit.thumbnail = escape(request.form['item-thumb'])
        else:
            itemToEdit.thumbnail = 'http://placehold.it/320x150'
        if request.form['item-pic']:
            itemToEdit.picture = escape(request.form['item-pic'])
        else:
            itemToEdit.picture = 'http://placehold.it/173x195'
        if request.form['item-cat']:
            itemToEdit.category_id = request.form['item-cat']
        if request.form['item-desc']:
            itemToEdit.description = escape(request.form['item-desc'])
        session.add(itemToEdit)
        session.commit()
        flash('{0} was successfully updated.'.format(itemToEdit.name))
        return redirect(url_for('showCategory', cat_name=itemToEdit.category.name))
    else:
        categories = getCategories()
        return render_template('edititem.html', item=itemToEdit, categories=categories)


@app.route('/catalog/<cat_name>/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(cat_name, item_name):
    if 'username' not in login_session:
        return redirect('catalog/login')
    itemToDelete = getItem(item_name)
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit
        flash("Item successfully deleted.")
        return redirect(url_for('showCategory', cat_name=cat_name))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


# Error handling routes
@app.errorhandler(400)
def NotFound(error):
    return render_template('400.html', message=error), 400


@app.errorhandler(404)
def NotFound(error):
    return render_template('404.html', message=error), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# Various helper functions
def getCategory(cat_name):
    try:
        category = session.query(Category).filter_by(name=cat_name).one()
        return category
    except:
        return []


def getCategoryById(cat_id):
    try:
        cat_id = session.query(Category).filter_by(id=cat_id).one()
        return cat_id
    except:
        return []


def getCategories():
    categories = session.query(Category).order_by(Category.name).all()
    return categories


def getAllItems():
    try:
        items = session.query(Item).all()
        return items
    except:
        return []


def getItems(category):
    try:
        category = session.query(Category).filter_by(name=category).one()
        items = session.query(Item).filter_by(category=category).all()
        return items
    except:
        return []


def getItem(item_name):
    try:
        item = session.query(Item).filter_by(name=item_name).one()
        return item
    except:
        return []


def createUser(login_session):
    newUser = User(name=login_session['username'], 
                   email=login_session['email'], 
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def generateRSS():
    rss_items = []
    items = getAllItems()
    for i in items:
        category = getCategoryById(i.category_id)
        url = url_for('showItem', cat_name=category.name, item_name=i.name)
        ri = PyRSS2Gen.RSSItem(title=i.name,
                               link=HOST + url,
                               description=i.description)
        rss_items.append(ri)

    rss = PyRSS2Gen.RSS2(
    title = "Item Imporium's RSS Feed",
    link = "{0}/catalog".format(HOST),
    description = "The latest items from the Item Imporium ",
    lastBuildDate = datetime.datetime.utcnow(),
    items = rss_items)
    #rss.write_xml(open("rss.xml", "w"))
    return rss


if __name__ == '__main__':
    # os.urandam(24)
    app.secret_key = 'S\xbe\x83U\xd1p{r\xef\xeaT\x96L\xaa\xefb\xd0\x90\xc9\xd1%\xf3\x19\xb8\xe9'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
