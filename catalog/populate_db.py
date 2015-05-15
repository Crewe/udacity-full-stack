# populate_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = creat_engine('sqlite:///reastaurantmenu.db')
DBSession = sessionmaker(bind = engine)
Base.metadata.bind = engine

newRestaurant = Reastaurant(name = "The Hip Spot")
session.add(newRestaurant)
session.commit()
session.query(Restaurant).all()
