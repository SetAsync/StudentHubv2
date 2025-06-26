from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import db, User, Question, CourseEntry, Course, QuestionReplies
import uuid, formatting
QuestionBlueprint = Blueprint('questionBoard', __name__, url_prefix="/")

@QuestionBlueprint.route('/questions/')
def questions():
    if "studentNumber" not in session.keys():
        return redirect(url_for("auth.signin"))
    
    studentCourses = CourseEntry.query.filter_by(studentNumber = session["studentNumber"]).all()
    if not studentCourses:
        flash("You don't take part in any courses!")
        return redirect(url_for("index"))
    
    studentQuestions = Question.query.filter_by(authorStudentNumber = session["studentNumber"]).all()
    otherQuestions = Question.query.filter(Question.authorStudentNumber != session["studentNumber"]).all()
    
    return render_template(
        "questionboard.html",
            StudentQuestions = studentQuestions, 
            PublicQuestions = otherQuestions, 
            StudentCourses = studentCourses
        )

@QuestionBlueprint.route('/question/<string:postid>')
def question(postid):
    if "studentNumber" not in session.keys():
        return redirect(url_for("auth.signin"))
    
    studentCourses = CourseEntry.query.filter_by(studentNumber = session["studentNumber"]).all()
    if not studentCourses:
        flash("You don't take part in any courses!")
        return redirect(url_for("index"))
    
    post = Question.query.filter_by(questionId = postid).first()
    replies = QuestionReplies.query.filter_by(questionId = postid).all()

    postHTML = formatting.render_markdown(post.postContent)

    if not post:
        flash("Invalid post!")
        return redirect(url_for("questionBoard.questions"))

    return render_template("question.html", post=post, replies = replies, postHTML = postHTML)

@QuestionBlueprint.route('/askquestion/', methods=['GET', 'POST'])
def askquestion():
    if "studentNumber" not in session:
        return redirect(url_for("auth.signin"))
    studentProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()

    studentCourseEntries = CourseEntry.query.filter_by(studentNumber=session["studentNumber"]).all()
    if not studentCourseEntries:
        flash("You don't take part in any courses!")
        return redirect(url_for("index"))

    studentCourses = [Course.query.filter_by(courseNumber=v.courseID).first() for v in studentCourseEntries]

    if request.method == 'POST':
        postTitle = request.form.get("postTitle")
        postContent = request.form.get("postContent")
        courseNumber = request.form.get("course")

        if not all([postTitle, postContent, courseNumber]):
            flash("Please fill out all fields.")
            return render_template("newQuestion.html", CourseList=studentCourses)

        new_question = Question(
            questionId=str(uuid.uuid4()),
            courseNumber=courseNumber,
            authorStudentNumber=session["studentNumber"],
            authorName=studentProfile.firstName,
            postTitle=postTitle,
            postContent=postContent,
            postStatus=0  # Awaiting Tutor
        )
        db.session.add(new_question)
        db.session.commit()

        flash("Your question has been posted.")
        return redirect(url_for("questionBoard.question", postid = new_question.questionId))

    return render_template("newQuestion.html", CourseList=studentCourses)

@QuestionBlueprint.route("/postreply/", methods=["POST"])
def postreply():
    if "studentNumber" not in session:
        return redirect(url_for("auth.signin"))
    studentProfile = User.query.filter_by(studentNumber = session["studentNumber"]).first()
    
    replyContent = request.form.get("replyContent")
    postID = request.form.get("questionId")
    if not all([replyContent, postID]):
        flash("Missing fields!")
        return redirect(url_for("questionBoard.questions"))
    
    newReply = QuestionReplies(
        replyId = str(uuid.uuid4()),
        questionId = postID,
        authorStudentName = studentProfile.firstName,
        authorStudentNumber = studentProfile.studentNumber,
        content = replyContent
    )
    db.session.add(newReply)
    db.session.commit()

    flash("Your reply has been posted.")
    return redirect(url_for("questionBoard.question", postid = postID))