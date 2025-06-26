from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import db, User, Question, CourseEntry, Course, QuestionReplies, Task
import uuid, formatting

TaskBlueprint = Blueprint('task', __name__, url_prefix="/")

@TaskBlueprint.route("/tasks")
def tasks():
    if "studentNumber" not in session.keys():
        return redirect(url_for("auth.signin"))
    
    tasks = Task.query.filter_by(studentNumber = session["studentNumber"]).all()

    return render_template("tasklist.html", tasks = tasks)


@TaskBlueprint.route("/viewtask/<string:taskid>")
def viewtask(taskid):
    if "studentNumber" not in session.keys():
        return redirect(url_for("auth.signin"))
    
    RequestedTask = Task.query.filter_by(taskId = taskid).first()
    if not RequestedTask:
        flash("404 - Task not found.", "error")
        return redirect(url_for("task.tasks"))
    
    Replies = QuestionReplies.query.filter_by(questionId = taskid).all()
    taskContent = formatting.render_markdown(RequestedTask.taskContent)

    return render_template("task.html", task = RequestedTask, replies = Replies, taskHTML = taskContent)

@TaskBlueprint.route("/posttaskreply/", methods=["POST"])
def posttaskreply():
    if "studentNumber" not in session:
        return redirect(url_for("auth.signin"))
    studentProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    
    replyContent = request.form.get("replyContent")
    taskID = request.form.get("taskId")
    if not all([replyContent, taskID]):
        flash("Missing fields!")
        return redirect(url_for("task.tasklist"))
    
    newReply = QuestionReplies(
        replyId = str(uuid.uuid4()),
        questionId = taskID,
        authorStudentName = studentProfile.firstName,
        authorStudentNumber = studentProfile.studentNumber,
        content = replyContent
    )
    db.session.add(newReply)
    db.session.commit()

    flash("Your reply has been posted.")
    return redirect(url_for("task.viewtask", taskid = taskID))