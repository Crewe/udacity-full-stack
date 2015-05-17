# populate_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

newRestaurant = Restaurant(name = "The Hip Spot")
session.add(newRestaurant)
session.commit()
session.query(Restaurant).all()
