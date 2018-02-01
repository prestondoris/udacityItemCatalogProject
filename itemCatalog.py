from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Users, Brewery, Beer

engine = create_engine('sqlite:///brewerycatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
@app.route('/login')
def login():
    return '''This is the landing page where users can login. Any change
        requests to items in the DB will be redirected to this page.'''


@app.route('/breweries')
def breweries():
    return 'This is the page that lists all the breweries in the catalog'


@app.route('/breweries/<int:id>/update')
def update_breweries(id):
    return '''This is the page that allows a signed in user that created the
        brewery to update and or delete given brewery in the database. They can
        only edit or delete items that they created. They will not be able to
        edit or delete any breweries that they did not create. If a user that
        is not logged in wants to view this page they will not have access'''


@app.route('/breweries/create')
def create_brewery():
    return '''This is the page that allows a signed in user to create a new
        brewery in the database. If a user who is not signed in wants to create
        a new brewery they will be taken back to the login page.'''

@app.route('/breweries/beers')
def beers():
    return '''This is the page that displays all the beers in the database for
        a given brewery'''


@app.route('/breweries/beers/<int:id>/update')
def update_beers(id):
    return '''This is the page that allows a signed in user that created the
        beer to update and or delete given beer in the database. They can
        only edit or delete items that they created. They will not be able to
        edit or delete any beers that they did not create. If a user that
        is not logged in wants to view this page they will not have access'''


@app.route('/breweries/beers/create')
def create_beer():
    return '''This is the page that allows a signed in user to create a new
        beer in the database. If a user who is not signed in wants to create
        a new beer they will be taken back to the login page.'''


def runApp():
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port=8000)


if __name__ == '__main__':
    runApp()
