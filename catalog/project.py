from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#REST Endpoint for a restaurant menu
@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuitems = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
    return jsonify(MenuItems = [i.serialize for i in menuitems])

 
#REST Endpoint for a restaurant menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuitem = session.query(MenuItem).filter_by(restaurant_id = restaurant.id, id = menu_id).one()
    return jsonify(MenuItem = menuitem.serialize)


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>')
def defaultRestaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('menu.html', restaurant = restaurant, items = items)


@app.route('/restaurants/<int:restaurant_id>/item/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['itemName'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New Menu Item Created!")
        return redirect(url_for('defaultRestaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/item/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['itemName']:
            menuItem.name = request.form['itemName']
        session.add(menuItem)
        session.commit()
        flash("Menu Item Updated!")
        return redirect(url_for('defaultRestaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menuItem = menuItem)


@app.route('/restaurants/<int:restaurant_id>/item/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(menuItem)
        session.commit()
        flash("Menu Item Deleted!")
        return redirect(url_for('defaultRestaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuitem.html', item = menuItem, restaurant_id = restaurant_id)


if __name__ == '__main__':
    app.secret_key = 'Super Secret Key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
