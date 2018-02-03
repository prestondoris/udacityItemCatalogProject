from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Users, Brewery, Beer
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2, json, random, string, requests
from flask import make_response


engine = create_engine('sqlite:///brewerycatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

@app.route('/')
@app.route('/login')
def login():
    # This is creating a randomized 32 character string that is unique for each
    # page load. This will be used to confirm that a user is actually a user
    # that there is not an Request attack taking place.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
                    
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods = ['POST'])
def googleSignin():
    # Validate State token created when user vistis login page. This token is
    # stored in login_session under the 'state' key. This will prevent
    # Anti-Forgery Request Attacks
    if request.args.get('state') != login_session['state']:
        serv_resp = make_response(json.dumps({'Invaild state parameter'}), 401)
        serv_resp.headers['Content-Type'] = 'application/json'
        return response
    auth_code = request.data


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
