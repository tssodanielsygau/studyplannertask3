from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


# Google API imports
import os
import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

auth = Blueprint('auth', __name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Allow HTTP for local testing

# -------------------------
# USER AUTH ROUTES
# -------------------------

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

# GOOGLE CALENDAR INTEGRATION

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


@auth.route('/authorize')
@login_required
def authorize():
    flow = Flow.from_client_secrets_file(
        'website/credentials.json',
        scopes=SCOPES,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(auth_url)


@auth.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'website/credentials.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    flash('Google account linked successfully!', category='success')
    return redirect(url_for('views.calendar'))


@auth.route('/create-event', methods=['POST'])
@login_required
def create_event():
    data = request.get_json()
    creds = Credentials.from_authorized_user_file('credentials.json')

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': data['summary'],
        'description': data.get('description', ''),
        'start': {
            'dateTime': data['start']['dateTime'],
            'timeZone': data['start']['timeZone'],
        },
        'end': {
            'dateTime': data['end']['dateTime'],
            'timeZone': data['end']['timeZone'],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify({'message': 'Event created successfully'})

def credentials_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

def build_credentials(creds_dict):
    return Credentials(
        token=creds_dict['token'],
        refresh_token=creds_dict['refresh_token'],
        token_uri=creds_dict['token_uri'],
        client_id=creds_dict['client_id'],
        client_secret=creds_dict['client_secret'],
        scopes=creds_dict['scopes']
    )
