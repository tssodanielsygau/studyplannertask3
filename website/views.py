from flask import Blueprint, render_template, request, flash, jsonify, session
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

views = Blueprint('views', __name__)

@views.route('/create-event', methods=['POST'])
@login_required
def create_event():
    try:
        data = request.get_json()
        creds = Credentials(**session['credentials'])  # Use session-stored credentials

        service = build("calendar", "v3", credentials=creds)

        event = {
            'summary': data.get("summary"),
            'description': data.get("description"),
            'start': {
                'dateTime': data.get("start")["dateTime"],
                'timeZone': 'Australia/Sydney',
            },
            'end': {
                'dateTime': data.get("end")["dateTime"],
                'timeZone': 'Australia/Sydney',
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        session['credentials'] = creds_to_dict(creds)  # Refresh stored credentials if updated

        return jsonify({"message": f"✅ Event created: {created_event.get('htmlLink')}"})

    except Exception as e:
        print("Error creating event:", e)
        return jsonify({"message": "❌ Failed to create event"}), 500

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/calendar')
@login_required
def calendar():
    return render_template("calendar.html", user=current_user)

@views.route('/add-note', methods=['POST'])
@login_required
def add_note():
    data = request.get_json()
    note_text = data.get('note', '').strip()

    if note_text:
        new_note = Note(data=note_text, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({"success": True, "note": note_text, "id": new_note.id})
    return jsonify({"success": False}), 400

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    data = request.get_json()
    note_id = data.get('noteId')
    note = Note.query.get(note_id)

    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False}), 400