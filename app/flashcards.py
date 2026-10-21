from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Flashcard, Note
from app.forms import CardReviewForm, EmptyForm
from app.services.srs import calculate_sm2

flashcards_bp = Blueprint("flashcards", __name__, url_prefix="/flashcards")


@flashcards_bp.route("", methods=["GET"])
@login_required
def index():
    today = date.today()
    all_cards = (
        Flashcard.query.filter_by(user_id=current_user.id)
        .order_by(Flashcard.created_at.desc())
        .all()
    )
    due_cards = [c for c in all_cards if c.due_date <= today]

    # Group cards by note
    notes_with_cards = (
        db.session.query(Note)
        .join(Flashcard, Flashcard.note_id == Note.id)
        .filter(Note.user_id == current_user.id)
        .distinct()
        .all()
    )

    return render_template(
        "flashcards/index.html",
        all_cards=all_cards,
        due_cards=due_cards,
        notes=notes_with_cards,
        today=today
    )


@flashcards_bp.route("/review", methods=["GET", "POST"])
@login_required
def review():
    today = date.today()
    form = CardReviewForm()

    if form.validate_on_submit():
        card_id = int(form.card_id.data)
        grade = int(form.grade.data)

        card = Flashcard.query.filter_by(id=card_id, user_id=current_user.id).first()
        if not card:
            abort(404)

        reps, interval, ef, new_due = calculate_sm2(
            grade=grade,
            repetitions=card.repetitions,
            interval_days=card.interval_days,
            ease_factor=card.ease_factor,
            today=today
        )

        card.repetitions = reps
        card.interval_days = interval
        card.ease_factor = ef
        card.due_date = new_due

        # Update user's study streak
        current_user.record_study_activity(today=today)
        db.session.commit()

        flash(f"Card reviewed! Next due in {interval} day(s).", "success")
        return redirect(url_for("flashcards.review"))

    # Fetch next due card
    due_card = (
        Flashcard.query.filter(
            Flashcard.user_id == current_user.id,
            Flashcard.due_date <= today
        )
        .order_by(Flashcard.due_date.asc(), Flashcard.id.asc())
        .first()
    )

    total_due = Flashcard.query.filter(
        Flashcard.user_id == current_user.id,
        Flashcard.due_date <= today
    ).count()

    return render_template(
        "flashcards/review.html",
        card=due_card,
        total_due=total_due,
        form=form
    )
