import datetime
import os
import pickle
from flask import Blueprint, redirect, url_for, session, request, render_template
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

calendar_bp = Blueprint('calendar', __name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'

@calendar_bp.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar.oauth2callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@calendar_bp.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar.oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    session['credentials'] = creds_to_dict(creds)
    return redirect(url_for('calendar.events'))

@calendar_bp.route('/events')
def events():
    creds = None
    if 'credentials' in session:
        creds = session['credentials']
    else:
        return redirect(url_for('calendar.authorize'))

    service = build('calendar', 'v3', credentials=build_credentials(creds))

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=5, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return render_template('events.html', events=events)

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

def build_credentials(session_creds):
    from google.oauth2.credentials import Credentials
    return Credentials(**session_creds)
