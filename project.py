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

APPLICATION_NAME = "Item Catalog Application"
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/catalog.json')
def catalogJSON():
    catalog=[]
    categories = getCategories()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/')
@app.route('/catalog')
def showCatalog():
    # Show 10 most recent items
    return render_template('index.html')


@app.route('/catalog/<cat_name>/items')
def showCategory(cat_name):
    # Show the items within a category
    return "Items in {0} category.".format(cat_name)
    return render_template('category.html')


@app.route('/catalog/<cat_name>/<item_name>/details')
def showItem(cat_name, item_name):
    # Show the detalis about an item
    return "{1} in the {0} category.".format(cat_name, item_name)
    return render_template('item.html')


# Error handling routes
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500


def getCategories():
    categories = session.query(Category).order_by(Category.name).all()
    return categories


def getItems(category):
    items = session.query(Item).filter_by(category=category).all()
    return items


if __name__ == '__main__':
    # os.urandam(24)
    app.secret_key = 'S\xbe\x83U\xd1p{r\xef\xeaT\x96L\xaa\xefb\xd0\x90\xc9\xd1%\xf3\x19\xb8\xe9'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
