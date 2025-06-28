from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    studentNumber = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    discordIdentifier = db.Column(db.String(50), nullable=True)
    passwordHash = db.Column(db.String(128), nullable=False)  # Store hashed password
    role = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"<User {self.studentNumber} - {self.firstName} {self.lastName}>"

class CourseEntry(db.Model):
    __tablename__ = "courseEntries"

    studentNumber = db.Column(db.String, primary_key=True, nullable=False)
    courseID = db.Column(db.String, primary_key=True, nullable=False)

class LoyaltyPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    studentNumber = db.Column(db.String, nullable=False)
    tutorName = db.Column(db.String, primary_key=False, nullable=False)
    currentBalance = db.Column(db.Integer, primary_key=False, nullable=False)

class Course(db.Model):
    courseNumber = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    courseName = db.Column(db.String, primary_key=False, unique=True, nullable=False)
    bookingUrl = db.Column(db.String, primary_key=False, unique=True, nullable=False)

class CourseResource(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    courseID = db.Column(db.Integer, autoincrement=True, nullable=False)
    resourceName = db.Column(db.String, nullable=False)
    resourceLink = db.Column(db.String, nullable=False)

class Question(db.Model):
    questionId = db.Column(db.String, primary_key = True, nullable=False)
    courseNumber = db.Column(db.String, nullable=False)
    authorStudentNumber = db.Column(db.String, nullable=False)
    authorName = db.Column(db.String, nullable=False)
    postTitle = db.Column(db.String, nullable=False)
    postContent = db.Column(db.String, nullable=False)
    postStatus = db.Column(db.Integer, nullable=False) # 0 - Awaiting Tutor, # 1 - Awaiting Student, # 2 - Resolved

class QuestionReplies(db.Model):
    replyId = db.Column(db.String, primary_key = True, nullable=False)
    questionId = db.Column(db.String, nullable=False)
    authorStudentName = db.Column(db.String, nullable=False)
    authorStudentNumber = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)

class Task(db.Model):
    taskId = db.Column(db.String, primary_key = True, nullable=False)
    tutor = db.Column(db.Integer, nullable = False)
    tutorName = db.Column(db.String, nullable = False)
    studentNumber = db.Column(db.Integer, nullable = False)
    taskTitle = db.Column(db.String, nullable = False)
    taskContent = db.Column(db.String, nullable = False)

class StudentNote(db.Model):
    noteId = db.Column(db.String, primary_key = True, nullable = False)
    studentId = db.Column(db.Integer, nullable = False)
    tutorId = db.Column(db.Integer, nullable = False)
    visibility = db.Column(db.Integer, nullable = False)
    authorName = db.Column(db.String, nullable = False)
    noteContent = db.Column(db.String, nullable = False)