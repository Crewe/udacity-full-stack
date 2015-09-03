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


class User(Base):
    # Table to describe the users of the system
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serializable(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Restaurant(Base):
    # Table to be ref'd in the database (must match the self.__name__)
    __tablename__ = 'restaurant'
    # Table mapping informaiton
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return a serialized object in JSON
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }


class MenuItem(Base):
    # Table to be ref'd in the database (must match the self.__name__)
    __tablename__ = 'menu_item'
    # Table mapping information
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    restaurant = relationship(Restaurant)
    user = relationship(User)

    @property
    def serialize(self):
        # Returns the serialized object as JSON
        return {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'description':  self.description,
            'price': self.price,
            'user_id': self.user_id,
        }

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
