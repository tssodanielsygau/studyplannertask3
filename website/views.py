from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Event
from . import db
from datetime import datetime
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Handle JSON AJAX Note Submission
    if request.is_json:
        data = request.get_json()
        note_text = data.get('note', '').strip()
        if len(note_text) < 1:
            return jsonify({'success': False, 'error': 'Note too short'})
        new_note = Note(data=note_text, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'success': True, 'note_id': new_note.id})

    # Handle AJAX Event Form Submission
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        title = request.form.get("event_title")
        date_str = request.form.get("event_date")
        time = request.form.get("event_time")
        location = request.form.get("event_location")
        description = request.form.get("event_description")

        if not title or not date_str:
            return jsonify({'success': False, 'error': 'Title and date required'})

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'})

        new_event = Event(
            title=title,
            date=date,
            time=time,
            location=location,
            description=description,
            user_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()

        # Return rendered event card HTML
        html = render_template("event_card.html", event=new_event)
        return jsonify({'success': True, 'html': html})

    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.date).all()
    return render_template("home.html", user=current_user, events=events)

@views.route('/delete-event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form.get("event_id")
    event = Event.query.get(event_id)
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted.", "success")
    return redirect(url_for("views.home"))

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    data = json.loads(request.data)
    note_id = data.get('noteId')
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        return jsonify(success=True)
    return jsonify({'error': 'Unauthorized'}), 403

@views.route('/edit-event/<int:id>', methods=['POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    if event.user_id != current_user.id:
        flash("Unauthorized", "error")
        return redirect(url_for('views.home'))

    title = request.form.get('event_title')
    date_str = request.form.get('event_date')
    time = request.form.get('event_time')
    location = request.form.get('event_location')

    try:
        event.title = title
        event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        event.time = time
        event.location = location
        db.session.commit()
        flash("Event updated!", "success")
    except Exception as e:
        flash("Error updating event.", "error")

    return redirect(url_for('views.home'))