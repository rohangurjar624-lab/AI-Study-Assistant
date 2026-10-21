from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Quiz, Question, Attempt, AttemptAnswer, Note
from app.forms import EmptyForm

quiz_bp = Blueprint("quiz", __name__)


def get_user_quiz_or_404(quiz_id: int) -> Quiz:
    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first()
    if not quiz:
        abort(404)
    return quiz


def get_user_attempt_or_404(attempt_id: int) -> Attempt:
    attempt = Attempt.query.filter_by(id=attempt_id, user_id=current_user.id).first()
    if not attempt:
        abort(404)
    return attempt


@quiz_bp.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def take_quiz(quiz_id: int):
    quiz = get_user_quiz_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id.asc()).all()

    if not questions:
        flash("This quiz currently has no questions.", "warning")
        return redirect(url_for("notes.view_note", note_id=quiz.note_id))

    if request.method == "POST":
        score = 0
        total = len(questions)

        # Parse duration if provided by client timer
        duration_seconds = None
        try:
            duration_raw = request.form.get("duration_seconds")
            if duration_raw:
                duration_seconds = max(0, int(duration_raw))
        except (ValueError, TypeError):
            duration_seconds = None

        attempt = Attempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=0,
            total=total,
            duration_seconds=duration_seconds,
        )
        db.session.add(attempt)
        db.session.flush()

        for q in questions:
            field_name = f"q_{q.id}"
            user_val = request.form.get(field_name)

            selected_idx = None
            is_correct = False

            if user_val is not None and user_val.strip() != "":
                try:
                    selected_idx = int(user_val)
                    if 0 <= selected_idx < len(q.options):
                        if selected_idx == q.correct_index:
                            is_correct = True
                            score += 1
                    else:
                        # Out of range index treated as unanswered/wrong
                        selected_idx = None
                except ValueError:
                    selected_idx = None

            ans = AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_index=selected_idx,
                is_correct=is_correct,
            )
            db.session.add(ans)

        attempt.score = score
        current_user.record_study_activity()
        db.session.commit()

        flash(f"Quiz completed! You scored {score} out of {total} ({attempt.percentage}%).", "success")
        return redirect(url_for("quiz.quiz_attempt", attempt_id=attempt.id))

    # GET request: Render quiz questions WITHOUT exposing correct answers or explanations
    # Package only safe fields to guarantee zero leakage in template or JavaScript
    safe_questions = [
        {
            "id": q.id,
            "text": q.text,
            "options": q.options,
            "topic": q.topic
        }
        for q in questions
    ]
    empty_form = EmptyForm()

    return render_template(
        "quiz/take.html",
        quiz=quiz,
        questions=safe_questions,
        empty_form=empty_form
    )


@quiz_bp.route("/quiz/attempt/<int:attempt_id>", methods=["GET"])
@login_required
def quiz_attempt(attempt_id: int):
    attempt = get_user_attempt_or_404(attempt_id)
    answers = AttemptAnswer.query.filter_by(attempt_id=attempt.id).all()
    return render_template("quiz/result.html", attempt=attempt, answers=answers)


@quiz_bp.route("/quizzes", methods=["GET"])
@login_required
def list_quizzes():
    quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    attempts = Attempt.query.filter_by(user_id=current_user.id).order_by(Attempt.taken_at.desc()).limit(30).all()
    return render_template("quiz/history.html", quizzes=quizzes, attempts=attempts)
