from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.models import Note, Quiz, Question, Flashcard
from app.forms import NoteForm, QuizGenerateForm, FlashcardGenerateForm, EmptyForm
from app.services import extract, llm
from app.services.extract import ValidationError, ScannedPDFError, ExtractError
from datetime import date

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


def get_user_note_or_404(note_id: int) -> Note:
    """Fetches note belonging to current user or aborts with 404."""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
    if not note:
        abort(404)
    return note


@notes_bp.route("", methods=["GET"])
@login_required
def index():
    search_query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Note.query.filter_by(user_id=current_user.id)
    if search_query:
        query = query.filter(Note.title.ilike(f"%{search_query}%"))

    pagination = query.order_by(Note.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template(
        "notes/index.html",
        notes=pagination.items,
        pagination=pagination,
        search_query=search_query
    )


@notes_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", key_func=lambda: str(current_user.id))
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        uploaded_file = form.file.data
        pasted_text = (form.content.data or "").strip()

        content = ""
        source_type = "paste"
        original_filename = None

        try:
            if uploaded_file and uploaded_file.filename:
                content, original_filename, source_type = extract.extract_from_file(uploaded_file)
            elif pasted_text:
                content = extract.validate_text_length(pasted_text)
                source_type = "paste"
            else:
                flash("Please either paste your study notes or upload a .txt/.pdf file.", "warning")
                return render_template("notes/new.html", form=form)
        except ScannedPDFError as e:
            flash(str(e), "danger")
            return render_template("notes/new.html", form=form)
        except (ValidationError, ExtractError) as e:
            flash(str(e), "danger")
            return render_template("notes/new.html", form=form)
        except Exception as e:
            flash(f"An unexpected error occurred during document processing: {e}", "danger")
            return render_template("notes/new.html", form=form)

        # Generate summary and keywords
        summary = llm.summarize(content)
        keywords = llm.extract_keywords(content, n=10)

        note = Note(
            title=title,
            content=content,
            source_type=source_type,
            original_filename=original_filename,
            summary=summary,
            keywords=keywords,
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()

        flash("Note created and analyzed successfully!", "success")
        return redirect(url_for("notes.view_note", note_id=note.id))

    return render_template("notes/new.html", form=form)


@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def view_note(note_id: int):
    note = get_user_note_or_404(note_id)
    quiz_form = QuizGenerateForm()
    flashcard_form = FlashcardGenerateForm()
    empty_form = EmptyForm()
    return render_template(
        "notes/view.html",
        note=note,
        quiz_form=quiz_form,
        flashcard_form=flashcard_form,
        empty_form=empty_form
    )


@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id: int):
    note = get_user_note_or_404(note_id)
    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data.strip()
        new_content = (form.content.data or "").strip()
        if new_content:
            try:
                note.content = extract.validate_text_length(new_content)
            except ValidationError as e:
                flash(str(e), "danger")
                return render_template("notes/edit.html", form=form, note=note)

        db.session.commit()
        flash("Note updated successfully.", "success")
        return redirect(url_for("notes.view_note", note_id=note.id))

    return render_template("notes/edit.html", form=form, note=note)


@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id: int):
    note = get_user_note_or_404(note_id)
    form = EmptyForm()
    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()
        flash(f"Note '{note.title}' and associated materials deleted.", "info")
        return redirect(url_for("notes.index"))
    return redirect(url_for("notes.view_note", note_id=note.id))


@notes_bp.route("/<int:note_id>/regenerate", methods=["POST"])
@login_required
@limiter.limit("10/hour", key_func=lambda: str(current_user.id))
def regenerate_note(note_id: int):
    note = get_user_note_or_404(note_id)
    form = EmptyForm()
    if form.validate_on_submit():
        note.summary = llm.summarize(note.content)
        note.keywords = llm.extract_keywords(note.content, n=10)
        db.session.commit()
        flash("Summary and keywords re-generated successfully!", "success")
    return redirect(url_for("notes.view_note", note_id=note.id))


@notes_bp.route("/<int:note_id>/quiz/new", methods=["POST"])
@login_required
@limiter.limit("10/hour", key_func=lambda: str(current_user.id))
def create_quiz(note_id: int):
    note = get_user_note_or_404(note_id)
    form = QuizGenerateForm()

    count = 5
    if form.validate_on_submit():
        try:
            count = int(form.count.data)
        except (ValueError, TypeError):
            count = 5

    questions_data, engine_used = llm.generate_quiz_with_engine(note.content, n=count)

    quiz = Quiz(
        user_id=current_user.id,
        note_id=note.id,
        title=f"Quiz: {note.title}",
        engine_used=engine_used
    )
    db.session.add(quiz)
    db.session.flush()

    for q in questions_data:
        question = Question(
            quiz_id=quiz.id,
            text=q["text"],
            options=q["options"],
            correct_index=q["correct_index"],
            explanation=q["explanation"],
            topic=q.get("topic", "General")
        )
        db.session.add(question)

    db.session.commit()
    flash(f"Quiz generated using {engine_used.upper()} engine! Ready to test your knowledge.", "success")
    return redirect(url_for("quiz.take_quiz", quiz_id=quiz.id))


@notes_bp.route("/<int:note_id>/flashcards/new", methods=["POST"])
@login_required
@limiter.limit("10/hour", key_func=lambda: str(current_user.id))
def create_flashcards(note_id: int):
    note = get_user_note_or_404(note_id)
    form = FlashcardGenerateForm()

    count = 10
    if form.validate_on_submit():
        try:
            count = int(form.count.data)
        except (ValueError, TypeError):
            count = 10

    cards_data = llm.generate_flashcards(note.content, n=count)
    today = date.today()

    created_count = 0
    for card_item in cards_data:
        flashcard = Flashcard(
            user_id=current_user.id,
            note_id=note.id,
            front=card_item["front"],
            back=card_item["back"],
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=today
        )
        db.session.add(flashcard)
        created_count += 1

    db.session.commit()
    flash(f"Generated {created_count} flashcards for '{note.title}'. All ready for review!", "success")
    return redirect(url_for("flashcards.index"))
