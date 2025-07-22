from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Event
from . import db
import json
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Handle JS-based Note POST
        if request.is_json:
            data = request.get_json()
            note_text = data.get('note', '').strip()
            if len(note_text) < 1:
                return jsonify(success=False, error="Note too short.")
            new_note = Note(data=note_text, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()

            # Dynamically return note HTML
            note_html = f"""
            <li id="note-{new_note.id}">
                {new_note.data}
                <button onclick="deleteNote({new_note.id})">&times;</button>
            </li>
            """
            return jsonify(success=True, note_html=note_html)

        # Handle standard form submissions
        elif 'note' in request.form:
            note = request.form.get('note')
            if len(note) < 1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')
                return redirect(url_for('views.home'))

        elif 'event-title' in request.form:
            title = request.form.get('event-title')
            date = request.form.get('event-date')
            time = request.form.get('event-time')
            location = request.form.get('event-location')

            if len(title) < 1 or len(date) < 1:
                flash('Event title and date are required.', category='error')
            else:
                new_event = Event(name=title, date=date, time=time, location=location, user_id=current_user.id)
                db.session.add(new_event)
                db.session.commit()
                flash('Event added!', category='success')
                return redirect(url_for('views.home'))

    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.date, Event.time).all()
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
        return jsonify(success=True)
    return jsonify({'error': 'Unauthorized'}), 403

@views.route('/delete-event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form.get('event_id')
    event = Event.query.get(event_id)
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted.", "success")
    return redirect(url_for('views.home'))
