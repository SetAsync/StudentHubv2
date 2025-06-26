from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import db, User

AuthBlueprint = Blueprint('auth', __name__, url_prefix="/")

@AuthBlueprint.route('/signin/', methods=['GET', 'POST'])
def signin():
    if "studentNumber" in session.keys():
        flash("Sign out first! (At the bottom of the page.)")
        return redirect(url_for("index"))

    if request.method == 'POST':
        student_number = request.form.get('StudentNumber')
        password = request.form.get('Password')

        user = User.query.filter_by(studentNumber=student_number).first()

        if user and user.passwordHash == password:
            session['studentNumber'] = user.studentNumber
            return redirect(url_for('index'))
        else:
            flash('Invalid student number or password', 'error')

    return render_template('signin.html')

@AuthBlueprint.route('/signout/', methods=['GET', 'POST'])
def signout():
    session.clear()
    flash("Signed out!", "info")
    return redirect(url_for("auth.signin"))