from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from datetime import datetime
from .auth import get_google_calendar_service
from dateutil.parser import parse as parse_date


views = Blueprint('views', __name__)

from dateutil.parser import parse as parse_date  # Add to your imports

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    events = []

    if request.method == 'POST': 
        note = request.form.get('note')
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            return redirect(url_for('views.home'))

    try:
        service = get_google_calendar_service()
        if service:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            raw_events = events_result.get('items', [])

            for e in raw_events:
                start_raw = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date')
                start_parsed = parse_date(start_raw).strftime("%a, %d %b %Y %I:%M %p") if "T" in start_raw else start_raw
                events.append({
                    'summary': e.get('summary', 'No Title'),
                    'start': start_parsed,
                    'location': e.get('location', 'No location')
                })
    except Exception as e:
        print(f"⚠️ Google Calendar error: {e}")

    return render_template("home.html", user=current_user, events=events)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data)
    note_id = note['noteId']
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({'error': 'Unauthorized'}), 403
