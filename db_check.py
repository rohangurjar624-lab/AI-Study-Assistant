from app import create_app
from app.extensions import db
from app.models import User, Note, Quiz, Question, Flashcard
from datetime import date

app = create_app()

with app.app_context():
    # 1. Clean previous check user
    old = User.query.filter_by(username="check_user").first()
    if old:
        db.session.delete(old)
        db.session.commit()

    # 2. Create test user
    user = User(username="check_user", email="check@example.com")
    user.set_password("SecureCheckPass123!")
    db.session.add(user)
    db.session.commit()

    # 3. Create note
    note = Note(
        title="Cellular Respiration",
        content="Cellular respiration is a set of metabolic reactions that convert chemical energy from nutrients into ATP.",
        source_type="paste",
        summary="Converts nutrients into ATP.",
        keywords=["ATP", "Respiration", "Energy"],
        owner=user
    )
    db.session.add(note)
    db.session.commit()

    # 4. Create Quiz
    quiz = Quiz(title="Quiz: Cellular Respiration", user=user, note=note)
    db.session.add(quiz)
    db.session.flush()

    q = Question(
        quiz_id=quiz.id,
        text="What molecule is primarily produced?",
        options=["ATP", "DNA", "Lipid", "Starch"],
        correct_index=0,
        explanation="ATP is cellular energy currency.",
        topic="Energy"
    )
    db.session.add(q)

    # 5. Create Flashcard
    fc = Flashcard(
        user=user,
        note=note,
        front="ATP",
        back="Adenosine triphosphate",
        due_date=date.today()
    )
    db.session.add(fc)
    db.session.commit()

    # 6. Verify assertions
    assert user.check_password("SecureCheckPass123!") is True
    assert user.check_password("WrongPassword") is False
    assert len(user.notes) == 1
    assert len(user.quizzes) == 1
    assert len(user.flashcards) == 1
    print("Database verification assertions passed successfully!")

    # 7. Test Cascade Delete
    db.session.delete(user)
    db.session.commit()
    assert Note.query.filter_by(title="Cellular Respiration").first() is None
    assert Quiz.query.filter_by(title="Quiz: Cellular Respiration").first() is None
    assert Question.query.filter_by(text="What molecule is primarily produced?").first() is None
    assert Flashcard.query.filter_by(front="ATP").first() is None
    print("Cascade delete verified successfully: all child entities cleaned up.")
