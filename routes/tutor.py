from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import db, User, Question, CourseEntry

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
    
    return '<img src="https://cdn.discordapp.com/attachments/1063918974695383100/1387469035691708517/Hn9wK5C.png?ex=685d74bc&is=685c233c&hm=f0b3e89697a6c702366a6372e3a2536af018e7ff8792137c075a84be5730a407&" alt="Image" />'