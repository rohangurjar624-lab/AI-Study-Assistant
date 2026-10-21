from datetime import date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Note, Quiz, Attempt, AttemptAnswer, Question, Flashcard

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    today = date.today()
    total_notes = Note.query.filter_by(user_id=current_user.id).count()
    attempts = Attempt.query.filter_by(user_id=current_user.id).order_by(Attempt.taken_at.desc()).all()
    total_quizzes = len(attempts)

    if total_quizzes > 0:
        avg_score = round(sum(a.percentage for a in attempts) / total_quizzes, 1)
        best_score = round(max(a.percentage for a in attempts), 1)
    else:
        avg_score = 0
        best_score = 0

    due_flashcards = Flashcard.query.filter(
        Flashcard.user_id == current_user.id,
        Flashcard.due_date <= today
    ).count()

    recent_notes = (
        Note.query.filter_by(user_id=current_user.id)
        .order_by(Note.created_at.desc())
        .limit(5)
        .all()
    )

    # Weak topics calculation
    topic_stats = (
        db.session.query(
            Question.topic,
            func.count(AttemptAnswer.id).label("total_answers"),
            func.sum(func.cast(AttemptAnswer.is_correct, db.Integer)).label("correct_answers"),
        )
        .join(AttemptAnswer, AttemptAnswer.question_id == Question.id)
        .join(Attempt, Attempt.id == AttemptAnswer.attempt_id)
        .filter(Attempt.user_id == current_user.id)
        .filter(Question.topic.isnot(None))
        .filter(Question.topic != "")
        .group_by(Question.topic)
        .all()
    )

    weak_topics = []
    for topic, total_ans, correct_ans in topic_stats:
        c_count = int(correct_ans or 0)
        t_count = int(total_ans or 0)
        if t_count > 0:
            accuracy = round((c_count / t_count) * 100, 1)
            weak_topics.append({
                "topic": topic,
                "accuracy": accuracy,
                "total": t_count,
                "correct": c_count,
            })

    # Sort lowest accuracy first
    weak_topics.sort(key=lambda x: (x["accuracy"], -x["total"]))

    return render_template(
        "dashboard/index.html",
        total_notes=total_notes,
        total_quizzes=total_quizzes,
        avg_score=avg_score,
        best_score=best_score,
        streak=current_user.streak_count,
        due_flashcards=due_flashcards,
        recent_notes=recent_notes,
        weak_topics=weak_topics[:5],
    )


@dashboard_bp.route("/dashboard/data", methods=["GET"])
@login_required
def dashboard_data():
    """Returns JSON analytics for Chart.js rendering (own data only)."""
    # Last 20 attempts for line chart (chronological order)
    recent_attempts = (
        Attempt.query.filter_by(user_id=current_user.id)
        .order_by(Attempt.taken_at.desc())
        .limit(20)
        .all()
    )
    # Reverse to show chronological progress
    recent_attempts.reverse()

    chart1_labels = [a.taken_at.strftime("%b %d, %H:%M") for a in recent_attempts]
    chart1_scores = [a.percentage for a in recent_attempts]

    # Bar chart: Average score per note
    note_attempts = (
        db.session.query(
            Note.title,
            func.avg((Attempt.score * 100.0) / Attempt.total).label("avg_pct"),
            func.count(Attempt.id).label("attempt_count")
        )
        .join(Quiz, Quiz.note_id == Note.id)
        .join(Attempt, Attempt.quiz_id == Quiz.id)
        .filter(Note.user_id == current_user.id)
        .group_by(Note.id, Note.title)
        .all()
    )

    chart2_labels = [row[0][:20] + ("..." if len(row[0]) > 20 else "") for row in note_attempts]
    chart2_scores = [round(float(row[1]), 1) for row in note_attempts]

    return jsonify({
        "chart1": {
            "labels": chart1_labels,
            "scores": chart1_scores
        },
        "chart2": {
            "labels": chart2_labels,
            "scores": chart2_scores
        }
    })
