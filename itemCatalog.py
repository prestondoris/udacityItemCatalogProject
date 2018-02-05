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


@app.route('/login')
def login():
    # This is creating a randomized 32 character string that is unique for each
    # page load. This will be used to confirm that a user is actually a user
    # that there is not an Request attack taking place.
    if 'name' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))

        login_session['state'] = state
        # return "The current session state is %s" % login_session['state']
        return render_template('login.html', STATE=state)
    else:
        return redirect(url_for('breweries'))



@app.route('/gconnect', methods = ['POST'])
def googleSignin():
    # Validate State token created when user vistis login page. This token is
    # stored in login_session under the 'state' key. This will prevent
    # Anti-Forgery Request Attacks
    if request.args.get('state') != login_session['state']:
        serv_resp = make_response(json.dumps('Invaild state parameter'), 401)
        serv_resp.headers['Content-Type'] = 'application/json'
        return serv_resp

    # Obtain authorization code from Google. This was sent to us by from the
    # AJAX POST request. We will use this auth_code to reach out to Google to
    # receive an access token which allows the server to make its own API calls.
    auth_code = request.data

    # Exchange the auth_code for credential tokens object. We will create a
    # try/except statement to account for potential errors allong the way.
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # This credentials object is the data that we exchanged our
        # auth_code for
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    print url
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this intended user.
    goog_id = credentials.id_token['sub']
    if result['user_id'] != goog_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if a user is already logged in.
    stored_access_token = login_session.get('access_token')
    stored_goog_id = login_session.get('goog_id')
    if stored_access_token is not None and goog_id == stored_goog_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['goog_id'] = goog_id

    # Get User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists in the DB, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '!</h1>'
    output += login_session['picture']
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output


@app.route('/glogout')
def googleLogout():
    # Only disconnect a connected user
    access_token = login_session['access_token']
    print access_token
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['goog_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']

        flash("You have successfully disconnected")
        return redirect(url_for('breweries'))
    else:
        flash("A 400 error occured. You are still logged in as %s") % login_session['name']
        return redirect(url_for('breweries'))


def createUser(login_session):
    newUser = Users(name=login_session['name'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/')
@app.route('/breweries')
def breweries():
    brewery = session.query(Brewery).all()
    if 'name' not in login_session:
        user = None
        return render_template('breweries.html', brewery = brewery, user = user)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('breweries.html', brewery = brewery, user = user)


@app.route('/breweries/<int:brewery_id>/update')
def update_breweries(brewery_id):
    """Route to update a brewery.

    This is the page that allows a signed in user that created the
    brewery to update and or delete given brewery in the database. They can
    only edit or delete items that they created. They will not be able to
    edit or delete any breweries that they did not create. If a user that
    is not logged in wants to view this page they will not have access

    Args:
        id: The id of the brewery

    Returns:
        Returns a rendered html template for updating and deleting a brewery

    """
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    if 'name' not in login_session:
        user = None
        return render_template('updateBrewery.html',
            brewery = brewery, user = user)
    else:
        creator = getUserInfo(brewery.user_id)
        user = getUserID(login_session['email'])
        if user == creator:
            return render_template('updateBrewery.html',
                brewery = brewery, user = user)
        else:
            # Need to finish this
            return None


@app.route('/breweries/create')
def create_brewery():
    """Route to create a new brewery

    This is the page that allows a signed in user to create a new
    brewery in the database. If a user who is not signed in wants to create
    a new brewery they will be taken back to the login page.
    Args:
        None
    Returns:
        Returns a rendered html template for creating a new brewery

    """
    if 'name' not in login_session:
        user = None
        return render_template('create_brewery.html', user=user)
    else:
        user = getUserID(login_session['email'])
        return render_template('create_brewery.html', user=user)



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
