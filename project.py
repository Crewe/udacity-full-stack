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
    return jsonify(Catalog=serializeCatalog())
    categories = getCategories()
    return jsonify(Categories=[c.serialize for c in categories])


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
        
    return render_template('item.html', item=item)


@app.route('/catalog/<cat_name>/item/add', methods=['GET', 'POST'])
def addItem(cat_name):
    category = getCategory(cat_name)
    categories = getCategories()
    if not category:
        return redirect('NotFound')
    if request.method == 'POST':
        try:
            print request
            print request.form
            newItem = Item(user_id=1,
                           name=escape(request.form['item-name']),
                           price=escape(request.form['item-price']),
                           thumbnail=escape(request.form['item-thumb']),
                           picture=escape(request.form['item-pic']),
                           category_id=request.form['item-cat'],
                           description=escape(request.form['item-desc']))
            session.add(newItem)
            session.commit()
            flash("Successfully added {0} to {1}!".format(newItem.name, category.name))
            return redirect(url_for('showCategory', cat_name=category.name))
        except:
            flash("Unable to add item to {0} category".format(category.name), 'error')
            return redirect(url_for('showCategory', cat_name=category.name))
    else:
        return render_template('additem.html', category=category, categories=categories)


@app.route('/catalog/<cat_name>/<item_name>/edit', methods=['GET', 'POST'])
def editItem(cat_name, item_name):
    itemToEdit = getItem(item_name)
    if request.method == 'POST':
        if request.form['item-name']:
            itemToEdit.name = escape(request.form['item-name'])
        if request.form['item-price']:
            itemToEdit.price = escape(request.form['item-price'])
        if request.form['item-thumb']:
            itemToEdit.thumbnail = escape(request.form['item-thumb'])
        if request.form['item-pic']:
            itemToEdit.picture = escape(request.form['item-pic'])
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


def getCategory(cat_name):
    try:
        category = session.query(Category).filter_by(name=cat_name).one()
        return category
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


def serializeCatalog():
    return {'nothing' : 'go away'}


if __name__ == '__main__':
    # os.urandam(24)
    app.secret_key = 'S\xbe\x83U\xd1p{r\xef\xeaT\x96L\xaa\xefb\xd0\x90\xc9\xd1%\xf3\x19\xb8\xe9'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
