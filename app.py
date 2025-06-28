from flask import Flask, render_template, session, redirect, flash, url_for
from db import db, User, CourseEntry, Course, CourseResource, LoyaltyPoints
import os

app = Flask(__name__)
app.secret_key = 'IzzyIsCute'

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'studenthub.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Load Blueprints
from routes import AuthBlueprint, QuestionBlueprint, TutorBlueprint, TaskBlueprint

for Blueprint in [AuthBlueprint, QuestionBlueprint, TutorBlueprint, TaskBlueprint]:
    app.register_blueprint(Blueprint)



@app.route('/')
def index():
    if "studentNumber" in session.keys():
        Student = User.query.filter_by(studentNumber = session["studentNumber"]).first()
        StudentResources = {}

        StudentCourses = CourseEntry.query.filter_by(studentNumber = Student.studentNumber).all()
        for v in StudentCourses:
            ThisCourse = Course.query.filter_by(courseNumber = v.courseID).first()
            ThisCourseResources = CourseResource.query.filter_by(courseID = v.courseID).all()
            StudentResources[ThisCourse.courseName] = ThisCourseResources


        RewardPoints = LoyaltyPoints.query.filter_by(studentNumber = Student.studentNumber).all()

        return render_template(
            "hub.html", 
            name = Student.firstName, 
            resources = StudentResources, 
            loyaltyData = RewardPoints,
            tutor = Student.role > 0
        )
    else:
        flash("You must be signed in to access this page!")
        return redirect(url_for("auth.signin"))

@app.before_request
def validate_student_session():
    student_number = session.get("studentNumber")

    if student_number:
        user = User.query.filter_by(studentNumber=student_number).first()
        if not user:
            # Student no longer exists in DB — log out and redirect
            session.clear()
            flash("Your account is no longer available.", "warning")
            return redirect(url_for("auth.signin"))

from markupsafe import Markup, escape

@app.template_filter('nl2br')
def nl2br(s):
    if not s:
        return ""
    escaped = escape(s)
    return Markup(escaped.replace('\n', '<br>'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created on first run
    app.run(debug=True)
