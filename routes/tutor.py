from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from db import db, User, StudentNote, Task
from sqlalchemy import or_
import trafft, uuid

TutorBlueprint = Blueprint('tutor', __name__, url_prefix="/")

@TutorBlueprint.route('/tutorhub/')
def tutorhub():
    if "studentNumber" not in session:
        flash("Please sign in!", "error")
        return redirect(url_for("auth.signin"))
    
    Account = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if Account.role < 1:
        flash("Access Denied! You are not a tutor/admin.", "error")
        return redirect(url_for("index"))
    
    return render_template("tutorhub.html")

@TutorBlueprint.route('/liveteach/')
def liveteach():
    if "studentNumber" not in session:
        flash("Please sign in!", "error")
        return redirect(url_for("auth.signin"))
    
    Account = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if Account.role < 1:
        flash("Access Denied! You are not a tutor/admin.", "error")
        return redirect(url_for("index"))
    
    return render_template("liveteach.html")

@TutorBlueprint.route("/golive/", methods=["GET", "POST"])
def golive():
    # Validate Profile
    if "studentNumber" not in session:
        flash("Please sign in!", "error")
        return redirect(url_for("auth.signin"))

    Account = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if Account.role < 1:
        flash("Access Denied! You are not a tutor/admin.", "error")
        return redirect(url_for("index"))

    # Fetch Appointment
    AppointmentID = request.form.get("appointmentId")
    if not AppointmentID.isdigit():
        flash("Invalid appointment!")
        return redirect(url_for("tutor.liveteach"))
    AppointmentID = int(AppointmentID)

    if AppointmentID > 9999:
        flash("Invalid appointment!")
        return redirect(url_for("tutor.liveteach"))

    Appointment = trafft.getAppointment(AppointmentID)
    if not Appointment:
        flash("Invalid appointment!")
        return redirect(url_for("tutor.liveteach"))

    # Validate Access
    TutorName = Appointment.employee.first_name + " " + Appointment.employee.last_name
    RequestingTutorName = Account.firstName + " " + Account.lastName
    if (Account.role == 1) and (TutorName != RequestingTutorName):
        flash("This appointment belogs to "+TutorName+"!", "error")
        return redirect(url_for("tutor.liveteach"))
    
    # Fetch TrafftClient Object
    StudentProfile = trafft.getClient(Appointment.bookings[0].customer.email)

    # Fetch Notes
    Notes = None

    if Account.role == 1:
        Notes = StudentNote.query.filter(
            StudentNote.studentId == StudentProfile.id,
            or_(
                StudentNote.tutorId == Account.studentNumber,
                StudentNote.visibility == 2
            )
        ).all()

        print(StudentProfile.id, Account.studentNumber)
    else:
        Notes = StudentNote.query.filter_by(
            studentId = StudentProfile.id
        ).all()

    print(Notes)

    return render_template(
        "golive.html", 
        appointment = Appointment, 
        client = StudentProfile, 
        notes = Notes
    )

# API: Save Summary / State
@TutorBlueprint.route("/saveLessonSummary", methods=['POST'])
def saveLessonSummary():
    data = request.get_json()
    if not all([data.get('summary_text'), data.get('action'), data.get('AppointmentID')]):
        return jsonify({
            "status": "error",
            "message": "Missing title or content"
        }), 400
    
    TutorProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if not (TutorProfile.role >= 1):
        return jsonify({
            "status": "error",
            "message": "Unauthorised"
        }), 403

    if data.get("action") == "send":
        Success = trafft.addNote(data.get('AppointmentID'), data.get('summary_text'))
        if not Success:
            return jsonify({
                "status": "error",
                "message": "error"
            }), 403

    return jsonify({"status": "success", "message": "Success!"})

# API: Destroy Note
@TutorBlueprint.route("/deleteNote", methods=['POST'])
def deleteNote():
    data = request.get_json()

    if not data or not data.get("noteId"):
        return jsonify({
            "status": "error",
            "message": "Missing title or content"
        }), 400
    
    TutorProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if not (TutorProfile.role >= 1):
        return jsonify({
            "status": "error",
            "message": "Unauthorised"
        }), 403
    
    note = StudentNote.query.filter_by(noteId = data.get("noteId")).first()
    if not note:
        return jsonify({
            "status": "error",
            "message": "Invalid"
        }), 404
    
    if (TutorProfile.role == 1) and (str(note.tutorId) != TutorProfile.studentNumber):
        return jsonify({
            "status": "error",
            "message": "Unauthorised"
        }), 403 
    
    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "success", "message": "success"})



# API: Create Note
@TutorBlueprint.route("/createNote", methods=['POST'])
def createNote():
    data = request.get_json()

    if not data or not data.get('client') or not data.get('noteText') or not data.get('noteVisibility'):
        return jsonify({
            "status": "error",
            "message": "Missing title or content"
        }), 400
    
    TutorProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if not (TutorProfile.role >= 1):
        return jsonify({
            "status": "error",
            "message": "Unauthorised"
        }), 403
    
    newNote = StudentNote(
        noteId = str(uuid.uuid4()),
        studentId = int(data.get("client")),
        tutorId = TutorProfile.studentNumber,
        visibility = int(data.get('noteVisibility')),
        authorName = TutorProfile.firstName + " " + TutorProfile.lastName,
        noteContent = data.get('noteText')
    )

    db.session.add(newNote)
    db.session.commit()


    return jsonify({"status": "success", "message": "success"})

# API: Create Assignment
@TutorBlueprint.route('/assignments', methods=['POST'])
def create_assignment():
    data = request.get_json()

    if not data or not data.get('assignment_title') or not data.get('assignment_content') or not data.get('client'):
        return jsonify({
            "status": "error",
            "message": "Missing title or content"
        }), 400

    TutorProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    if not TutorProfile.role >= 1:
        return jsonify({
            "status": "Unauthorised",
            "message": "Unauthorised"
        }), 403
    
    newTask = Task(
        taskId = str(uuid.uuid4()),
        tutor = TutorProfile.studentNumber,
        tutorName = TutorProfile.firstName + " " + TutorProfile.lastName,
        studentNumber = data.get('client'),
        taskTitle = data.get("assignment_title"),
        taskContent = data.get("assignment_content")
    )

    db.session.add(newTask)
    db.session.commit()


    return jsonify({"status": "success", "message": "Assignment created!"})