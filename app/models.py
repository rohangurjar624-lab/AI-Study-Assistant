from datetime import datetime, timezone, date, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    streak_count = db.Column(db.Integer, default=0, nullable=False)
    last_study_date = db.Column(db.Date, nullable=True)

    notes = db.relationship(
        "Note", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    quizzes = db.relationship(
        "Quiz", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    attempts = db.relationship(
        "Attempt", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    flashcards = db.relationship(
        "Flashcard", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def record_study_activity(self, today=None):
        if today is None:
            today = date.today()
        if self.last_study_date is None:
            self.streak_count = 1
            self.last_study_date = today
        elif self.last_study_date == today:
            pass  # Already studied today, maintain streak
        elif self.last_study_date == today - timedelta(days=1):
            self.streak_count += 1
            self.last_study_date = today
        else:
            # Missed at least one day
            self.streak_count = 1
            self.last_study_date = today

    def __repr__(self):
        return f"<User {self.username}>"


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type = db.Column(db.String(20), default="paste", nullable=False)  # paste, txt, pdf
    original_filename = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.JSON, nullable=True)

    quizzes = db.relationship(
        "Quiz", backref="note", lazy=True, cascade="all, delete-orphan"
    )
    flashcards = db.relationship(
        "Flashcard", backref="note", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Note {self.title}>"


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_id = db.Column(
        db.Integer, db.ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    engine_used = db.Column(db.String(20), default="offline", nullable=False)  # llm, offline

    questions = db.relationship(
        "Question", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )
    attempts = db.relationship(
        "Attempt", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Quiz {self.title}>"


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # list of 4 strings
    correct_index = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Question {self.id} for Quiz {self.quiz_id}>"


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    taken_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)

    answers = db.relationship(
        "AttemptAnswer", backref="attempt", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def percentage(self):
        if self.total == 0:
            return 0
        return round((self.score / self.total) * 100, 1)

    def __repr__(self):
        return f"<Attempt {self.id}: {self.score}/{self.total}>"


class AttemptAnswer(db.Model):
    __tablename__ = "attempt_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(
        db.Integer, db.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    selected_index = db.Column(db.Integer, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False)

    question = db.relationship("Question")

    def __repr__(self):
        return f"<AttemptAnswer q={self.question_id} correct={self.is_correct}>"


class Flashcard(db.Model):
    __tablename__ = "flashcards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_id = db.Column(
        db.Integer, db.ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    ease_factor = db.Column(db.Float, default=2.5, nullable=False)
    interval_days = db.Column(db.Integer, default=0, nullable=False)
    repetitions = db.Column(db.Integer, default=0, nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<Flashcard {self.id} due={self.due_date}>"
