from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Event, Reminder, Pomodoro, Grade
from . import db
from datetime import datetime, date, timedelta
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
        flash("Note added!", "success")
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
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'})

        new_event = Event(
            title=title,
            date=parsed_date,
            time=time,
            location=location,
            description=description,
            user_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()
        flash("Event added!", "success")

        html = render_template("event_card.html", event=new_event)
        return jsonify({'success': True, 'html': html, 'message': 'Event added!'})

    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.due_date).all()
    now = date.today()
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.date).all()
    grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.due_date).all()
    for grade in grades:
        if isinstance(grade.due_date, str):
            try:
                grade.due_date = datetime.strptime(grade.due_date, "%Y-%m-%d").date()
            except ValueError:
                pass

    return render_template("home.html", user=current_user, events=events, reminders=reminders, now=now, grades=grades)

@views.route('/delete-event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form.get("event_id")
    event = Event.query.get(event_id)
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted.", "success")
    else:
        flash("Event not found or unauthorized.", "error")
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
        flash("Note deleted.", "success")
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
    description = request.form.get('event_description')

    try:
        event.title = title
        event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        event.time = time
        event.location = location
        event.description = description
        db.session.commit()
        flash("Event updated!", "success")
    except Exception as e:
        flash("Error updating event.", "error")

    return redirect(url_for('views.home'))

@views.route('/add-reminder', methods=['POST'])
@login_required
def add_reminder():
    data = request.get_json()
    content = data.get("content", "").strip()
    due_str = data.get("due_date", "").strip()

    if not content or not due_str:
        return jsonify(success=False, error="Missing fields")

    try:
        due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify(success=False, error="Invalid date format")

    new_reminder = Reminder(content=content, due_date=due_date, user_id=current_user.id)
    db.session.add(new_reminder)
    db.session.commit()

    days_left = (due_date - date.today()).days
    flash("Reminder added!", "success")

    return jsonify(success=True, id=new_reminder.id, content=content, due=due_str, days_left=days_left)

@views.route('/delete-reminder', methods=['POST'])
@login_required
def delete_reminder():
    data = json.loads(request.data)
    reminder_id = data.get('id')
    reminder = Reminder.query.get(reminder_id)
    if reminder and reminder.user_id == current_user.id:
        db.session.delete(reminder)
        db.session.commit()
        flash("Reminder deleted.", "success")
        return jsonify(success=True)
    return jsonify({'error': 'Unauthorized'}), 403

@views.route("/start-pomodoro", methods=["POST"])
@login_required
def start_pomodoro():
    duration = int(request.form.get("duration", 25))
    new_session = Pomodoro(
        start_time=datetime.utcnow(),
        duration_minutes=duration,
        user_id=current_user.id
    )
    db.session.add(new_session)
    db.session.commit()
    flash(f"Pomodoro started for {duration} minutes!", "success")
    return redirect(url_for('views.home'))

@views.route("/check-pomodoro", methods=["GET"])
@login_required
def check_pomodoro():
    session = Pomodoro.query.filter_by(user_id=current_user.id).order_by(Pomodoro.start_time.desc()).first()
    if not session:
        return jsonify({"active": False})

    now = datetime.utcnow()
    end_time = session.start_time + timedelta(minutes=session.duration_minutes)
    remaining = (end_time - now).total_seconds()

    if remaining <= 0:
        return jsonify({"active": False, "message": "Session complete!"})

    return jsonify({
        "active": True,
        "minutes": int(remaining // 60),
        "seconds": int(remaining % 60)
    })
    
@views.route('/grades', methods=['GET'])
@login_required
def grades():
    grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.due_date).all()
    return render_template("grades.html", user=current_user, grades=grades)

@views.route('/add-grade', methods=['POST'])
@login_required
def add_grade():
    name = request.form.get("name")
    due_date = request.form.get("due_date")
    weighting = request.form.get("weighting")
    final_mark = request.form.get("final_mark")
    percentage = request.form.get("percentage")

    if not name or not due_date:
        flash("Please fill out all required fields.", "error")
        return redirect(url_for('views.grades'))

    new_grade = Grade(
        name=name,
        due_date=due_date,
        weighting=weighting,
        final_mark=final_mark,
        percentage=percentage,
        user_id=current_user.id
    )
    db.session.add(new_grade)
    db.session.commit()
    flash("Grade added!", "success")
    return redirect(url_for('views.grades'))

@views.route('/edit-grade/<int:grade_id>', methods=['POST'])
@login_required
def edit_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)

    if grade.user_id != current_user.id:
        flash("Unauthorized action", "error")
        return redirect(url_for('views.grades'))

    grade.name = request.form.get("name")
    grade.due_date = request.form.get("due_date")
    grade.weighting = request.form.get("weighting")
    grade.final_mark = request.form.get("final_mark")
    grade.percentage = request.form.get("percentage")

    db.session.commit()
    flash("Grade updated!", "success")
    return redirect(url_for('views.grades'))