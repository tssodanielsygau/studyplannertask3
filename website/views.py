from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from flask import request, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

views = Blueprint('views', __name__)

@views.route('/create-event', methods=['POST'])
@login_required
def create_event():
    try:
        data = request.get_json()

        # Example log (remove in prod)
        print("Received Event:", data)

        title = data.get("summary")
        description = data.get("description")
        start_time = data.get("start", {}).get("dateTime")
        end_time = data.get("end", {}).get("dateTime")

        # Here you would insert Google Calendar API logic

        # Example response
        return jsonify({"message": f"✅ Event '{title}' created successfully!"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "❌ Failed to create event"}), 500


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