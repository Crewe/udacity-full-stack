# database_setup.py
# Database configuration file for the ORM
#

import os
import sys
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Restaurant(Base):
	# Table to be ref'd in the database (must match the self.__name__)
	__tablename__ = 'restaurant'
	# Table mapping informaiton
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)


class MenuItem(Base):
	# Table to be ref'd in the database (must match the self.__name__)
	__tablename__ = 'menu_item'
	# Table mapping information 
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	course = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))
	restuarant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
