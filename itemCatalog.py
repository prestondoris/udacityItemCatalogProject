from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Users, Brewery, Beer
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import string
import requests


engine = create_engine('sqlite:///brewerycatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
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


@app.route('/gconnect', methods=['POST'])
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
    # receive an access token which allows the server to make its own API calls
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
        response = make_response(json.dumps('''Failed to upgrade the
                                            authorization code.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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
        response = make_response(json.dumps('''Current user is already
                                            connected.'''), 200)
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
    output += '<p>We are redirecting you, please wait.'
    return output


@app.route('/glogout')
def googleLogout():
    # Logout from Google
    #
    # This function will disconnect the user from the current session.
    #
    # Args:
    #   None
    #
    # Returns:
    #   If Successfull - redirect to breweries.html with flash message to
    #   to notify the user their were logged out.
    #
    #   If Unsuccessfull - redirect to breweries.html with flask message to
    #   to notify the user they were not logged out.

    # Only disconnect a connected user
    access_token = login_session['access_token']
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

        flash("You have successfully logged out")
        return redirect(url_for('breweries'))
    else:
        flash("A 400 error occured. You are still logged in")
        return redirect(url_for('breweries'))


def createUser(login_session):
    # Method for adding a new user to the DB
    #
    # Args:
    #   login_session - this is a list that contains all of login
    #   information of the logged in user.
    #
    # Returns:
    #   User.id - this is the DB generated id once the user has been added to
    #   the DB.

    newUser = Users(name=login_session['name'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    # Method for securing all of a users information from the DB
    #
    # Args:
    #   user_id - this is used to filter through the DB to return the single
    #   desired user.
    #
    # Returns:
    #   user - this is a list that contains all of the users information.

    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    # Method for securing a specific users id from the DB
    #
    # Args:
    #   email - this is used to filter through the DB to return the single
    #   desired user via their email.
    #
    # Returns:
    #   user.id - this is the id of the specific user

    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/breweries')
def breweries():
    breweries = session.query(Brewery).all()
    recent = session.query(Beer).all()
    recent.reverse()
    for i in recent:
        counter = len(recent)
        if counter > 4:
            recent = recent[:-1]
        else:
            break

    if 'name' not in login_session:
        user = None
        return render_template('breweries.html', breweries=breweries,
                               recent=recent, user=user)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('breweries.html', breweries=breweries,
                               recent=recent, user=user)


@app.route('/breweries/update/<int:brewery_id>', methods=['GET', 'POST'])
def update_brewery(brewery_id):
    # Route to update a brewery.
    #
    # This is the page that allows a signed in user that created the
    # brewery to update the given brewery in the database. They can
    # only edit items that they created. They will not be able to
    # edit any breweries that they did not create. If a user that
    # is not logged in wants to view this page they will not have access
    #
    # Args:
    #    id: The id of the brewery
    #
    # Returns:
    #    GET Requests:
    #        Returns a rendered html template for updating a
    #        brewery
    #    POST Requests:
    #        Receives the form data to update the brewery in the database,
    #        then returns a redirect to the main breweries page.

    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        creator = getUserInfo(brewery.user_id)
        user = getUserInfo(getUserID(login_session['email']))
        if user.id == creator.id:
            if request.method == 'POST':
                brewery.name = request.form['name']
                session.add(brewery)
                session.commit()
                flash('%s was successfully updated!' % brewery.name)
                return redirect(url_for('breweries'))
            else:
                return render_template('updateBrewery.html',
                                       brewery=brewery, user=user)
        else:
            flash('''You cannot update this brewery because you are not the
                  creator. Only the person who created a Brewery can
                  update it.''')
            return redirect(url_for('breweries'))


@app.route('/breweries/delete/<int:brewery_id>', methods=['GET', 'POST'])
def delete_brewery(brewery_id):
    # Route to delete a brewery.
    # This is the page that allows a signed in user that created the
    # brewery to delete the given brewery in the database. They can
    # only delete items that they created. They will not be able to
    # delete any breweries that they did not create. If a user that
    # is not logged in wants to view this page they will not have access
    # Args:
    #    id: The id of the brewery
    # Returns:
    #    GET Requests:
    #        Returns a rendered html template for deleting a
    #        brewery
    #    POST Requests:
    #        Receives the form data to delete the brewery from database, then
    #        returns a redirect to the main breweries page.

    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        creator = getUserInfo(brewery.user_id)
        user = getUserInfo(getUserID(login_session['email']))
        if user.id == creator.id:
            if request.method == 'POST':
                session.delete(brewery)
                flash('%s was successfully deleted!' % brewery.name)
                session.commit()
                return redirect(url_for('breweries'))
            else:
                return render_template('delete_brewery.html',
                                       brewery=brewery, user=user)
        else:
            flash('''You cannot delete this brewery because you are not the
                  creator. Only the person who created a Brewery can
                  delete it.''')
            return redirect(url_for('breweries'))


@app.route('/breweries/create', methods=['GET', 'POST'])
def create_brewery():
    # Route to create a new brewery
    #
    # This is the page that allows a signed in user to create a new
    # brewery in the database. If a user who is not signed in wants to create
    # a new brewery they will be taken back to the login page.
    #
    # Args:
    #    None
    # Returns:
    #    Returns a rendered html template for creating a new brewery

    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        user = getUserInfo(getUserID(login_session['email']))
        if request.method == 'POST':
            newBrewery = Brewery(name=request.form['name'], user_id=user.id)
            session.add(newBrewery)
            session.commit()
            flash("Thank you for creating a new brewery!!")
            return redirect(url_for('breweries'))
        else:
            return render_template('create_brewery.html', user=user)


@app.route('/breweries/<int:brewery_id>/beers')
def beers(brewery_id):
    # Route to display all beers in the database for a given brewery.
    #
    # Args:
    #   brewery_id - the id of the brewery the user clicked on. This is used to
    #   identify all the beers in the Beer table associated with that brewery.
    # Returns:
    #   render_template for the beers.html page.

    breweries = session.query(Brewery).all()
    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    beers = session.query(Beer).filter_by(brewery_id=brewery.id).all()
    if 'name' not in login_session:
        user = None
        return render_template('beers.html', breweries=breweries,
                               brewery=brewery, beers=beers, user=user)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('beers.html', breweries=breweries,
                               brewery=brewery, beers=beers, user=user)


@app.route('/breweries/<int:brewery_id>/beers/<int:beer_id>/update',
           methods=['GET', 'POST'])
def update_beer(brewery_id, beer_id):
    # Route to Update a beer
    #
    # Args:
    #   brewery_id - the id of the brewery the user clicked on. This is used to
    #   identify all the beers in the Beer table associated with that brewery.
    #   beer_id - the id of the specific beer to update
    # Returns:
    #   render_template for update_beer.html
    #   if user is not logged in then a redirect back to beers

    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    beer = session.query(Beer).filter_by(id=beer_id).one()
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        creator = getUserInfo(beer.user_id)
        user = getUserInfo(getUserID(login_session['email']))
        if user.id == creator.id:
            if request.method == 'POST':
                if request.form.get('name'):
                    beer.name = request.form.get('name')
                if request.form.get('style'):
                    beer.style = request.form.get('style')
                if request.form.get('description'):
                    beer.description = request.form.get('description')
                return redirect(url_for('beers', brewery_id=brewery.id))
            else:
                return render_template('update_beer.html',
                                       brewery=brewery, beer=beer, user=user)
        else:
            flash('''You cannot update this beer because you are not the
                  creator. Only the person who created a beer can
                  update it.''')
            return redirect(url_for('beers', brewery_id=brewery.id,
                                    beer_id=beer.id))


@app.route('/breweries/<int:brewery_id>/beers/<int:beer_id>/delete',
           methods=['GET', 'POST'])
def delete_beer(brewery_id, beer_id):
    # Route to the page to delete a beer from the DB
    #
    # Args:
    #   brewery_id - the id of the brewery the user clicked on. This is used to
    #   identify all the beers in the Beer table associated with that brewery.
    #   beer_id - the id of the specific beer to delete
    # Returns:
    #   render_template for delete_beer.html
    #   If user is not logged in then a redirect to beers

    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    beer = session.query(Beer).filter_by(id=beer_id).one()
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        creator = getUserInfo(beer.user_id)
        user = getUserInfo(getUserID(login_session['email']))
        if user.id == creator.id:
            if request.method == 'POST':
                session.delete(beer)
                session.commit()
                return redirect(url_for('beers', brewery_id=brewery.id))
            else:
                return render_template('delete_beer.html',
                                       brewery=brewery,
                                       beer=beer, user=user)
        else:
            flash('''You cannot delete this beer because you are not the
                  creator. Only the person who created a Beer can
                  delete it.''')
            return redirect(url_for('beers', brewery_id=brewery.id,
                                    beer_id=beer.id))


@app.route('/breweries/<int:brewery_id>/beers/create', methods=['GET', 'POST'])
def create_beer(brewery_id):
    # Route to create a beer
    #
    # Args:
    #   brewery_id - the id of the brewery the user clicked on. This is used to
    #   identify all the beers in the Beer table associated with that brewery.
    # Returns:
    #   render_template to create_beer
    #   if user is not logged in, then it takes them to the login page
    #   a redirect to beers after creating a beer

    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        user = getUserInfo(getUserID(login_session['email']))
        print user.id
        if request.method == 'POST':
            newBeer = Beer(name=request.form.get('name'),
                           style=request.form.get('style'),
                           description=request.form.get('description'),
                           user_id=user.id,
                           brewery_id=brewery.id)
            session.add(newBeer)
            session.commit()
            flash("Thank you for creating a new beer!")
            return redirect(url_for('beers', brewery_id=brewery.id))
        else:
            return render_template('create_beer.html',
                                   brewery=brewery, user=user)


@app.route('/api/breweries/')
def breweriesJSON():
    if 'name' not in login_session:
        return redirect(url_for('login'))
    else:
        items = session.query(Beer).all()
        return jsonify(Catalog=[i.serialize for i in items])


def runApp():
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    runApp()
