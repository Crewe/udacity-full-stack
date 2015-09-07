# seed_database.py
# Data to populate the database with.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, Item

# Create the DB and initialize engine
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

# Bind session to the engine so db calls are atomic
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a user
user1 = User(name="Crewe Wrecking", 
             picture='http://ryancrewe.com/imgs/avatars/sp_avatar.PNG',
             email='Wrecking.Crewe@mydomain.com')
session.add(user1)
session.commit()
print "User {0} added.".format(user1.name)


# Create Categories
cat1 = Category(user_id=1,
                name='Outdoors')
session.add(cat1)
session.commit()
print "Category {0} added.".format(cat1.name)

cat2 = Category(user_id=1,
                name='Indoors')
session.add(cat2)
session.commit()
print "Category {0} added.".format(cat2.name)

cat3 = Category(user_id=1,
                name='Entertainment')
session.add(cat3)
session.commit()
print "Category {0} added.".format(cat3.name)

cat4 = Category(user_id=1,
                name='Books')
session.add(cat4)
session.commit()
print "Category {0} added.".format(cat4.name)

cat5 = Category(user_id=1,
                name='Automotive')
session.add(cat5)
session.commit()
print "Category {0} added.".format(cat5.name)


# Create items
item1 = Item(user_id=1,
             category_id=1,
             name='Felt Bicycle',
             description='Felt F65X Cylclocross Bicycle.',
             price='$2048.32',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item1)
session.commit()
print "Item {0} added.".format(item1.name)

item2 = Item(user_id=1,
             category_id=2,
             name='Newport Propane Fireplace',
             description='Keep a small space nice and cozy warm with this 4500BTU/hr fireplace.',
             price='$650.78',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item2)
session.commit()
print "Item {0} added.".format(item2.name)

item3 = Item(user_id=1,
             category_id=3,
             name='Technics SL1200 Turntable',
             description='Get the wax spinnin\' and music groovin\'',
             price='$175.87',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item3)
session.commit()
print "Item {0} added.".format(item3.name)

item4 = Item(user_id=1,
             category_id=4,
             name='Thinking, Fast and Slow',
             description='By Daniel E. Kahneman',
             price='$9.99',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item4)
session.commit()
print "Item {0} added.".format(item4.name)

item5 = Item(user_id=1,
             category_id=4,
             name='The Power of Habbit',
             description='Why We Do What We Do in Life and Business. By Charles Duhigg',
             price='$29.99',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item5)
session.commit()
print "Item {0} added.".format(item5.name)

item6 = Item(user_id=1,
             category_id=3,
             name='The Stanley Parable',
             description='The Stanley Parable is an interactive story modification built on the Source game engine, designed by Davey Wreden, and released in July 2011',
             price='14.99',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item6)
session.commit()
print "Item {0} added.".format(item6.name)

item7 = Item(user_id=1,
             category_id=1,
             name='Tiny House by Small Footprint',
             description='A made to order 20 square-meter tiny house on a 2 axel square tube steel trailer. Just add yourself.',
             price='$48324.32',
             thumbnail='http://placehold.it/320x150',
             picture='http://placehold.it/173x195')
session.add(item7)
session.commit()
print "Item {0} added.".format(item7.name)
