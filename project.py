# project.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

APPLICATION_NAME = "Item Catalog Application"
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def showCatalog():
    return render_template('index.html')


if __name__ == '__main__':
    # os.urandam(24)
    app.secret_key = 'S\xbe\x83U\xd1p{r\xef\xeaT\x96L\xaa\xefb\xd0\x90\xc9\xd1%\xf3\x19\xb8\xe9'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
