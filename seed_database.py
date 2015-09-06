# seed_database.py
# Data to initialize the database with.

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

# Create items
item1 = Item(user_id=1,
             category_id=1,
             name='Felt Bicycle',
             description='Felt F65X Cylclocross Bicycle.',
             price='$2048.32',
             picture='')
session.add(item1)
session.commit()
print "Item {0} added.".format(item1.name)

item2 = Item(user_id=1,
             category_id=2,
             name='Newport Propane Fireplace',
             description='Keep a small space nice and cozy warm with this 4500BTU/hr fireplace.',
             price='$650.78',
             picture='')
session.add(item2)
session.commit()
print "Item {0} added.".format(item2.name)

item3 = Item(user_id=1,
             category_id=3,
             name='Technics SL1200 Turntable',
             description='Get the wax spinnin\' and music groovin\'',
             price='$175.87',
             picture='')
session.add(item3)
session.commit()
print "Item {0} added.".format(item3.name)

item4 = Item(user_id=1,
             category_id=4,
             name='Thinking, Fast and Slow',
             description='By Daniel E. Kahneman',
             price='$9.99',
             picture='')
session.add(item4)
session.commit()
print "Item {0} added.".format(item4.name)