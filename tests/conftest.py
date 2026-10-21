import pytest
from app import create_app
from app.extensions import db
from app.models import User, Note, Quiz, Question, Attempt, Flashcard
from datetime import date


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def auth_client(client, auth_user, app):
    client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=True)
    return client


@pytest.fixture
def two_users(app):
    with app.app_context():
        u1 = User(username="user_alpha", email="alpha@example.com")
        u1.set_password("password123")
        u2 = User(username="user_beta", email="beta@example.com")
        u2.set_password("password123")
        db.session.add_all([u1, u2])
        db.session.commit()

        # Alpha's note
        note_a = Note(
            title="Alpha Note",
            content="Alpha study content " * 20,
            user_id=u1.id,
            source_type="paste",
            summary="Alpha summary.",
            keywords=["Alpha", "Note"]
        )
        db.session.add(note_a)
        db.session.flush()

        quiz_a = Quiz(user_id=u1.id, note_id=note_a.id, title="Alpha Quiz", engine_used="offline")
        db.session.add(quiz_a)
        db.session.flush()

        q_a = Question(
            quiz_id=quiz_a.id,
            text="Alpha Question?",
            options=["A", "B", "C", "D"],
            correct_index=0,
            explanation="A is correct.",
            topic="AlphaTopic"
        )
        db.session.add(q_a)
        db.session.flush()

        att_a = Attempt(user_id=u1.id, quiz_id=quiz_a.id, score=1, total=1)
        db.session.add(att_a)

        fc_a = Flashcard(user_id=u1.id, note_id=note_a.id, front="AlphaFront", back="AlphaBack", due_date=date.today())
        db.session.add(fc_a)

        # Beta's note
        note_b = Note(
            title="Beta Note",
            content="Beta study content " * 20,
            user_id=u2.id,
            source_type="paste",
            summary="Beta summary.",
            keywords=["Beta", "Note"]
        )
        db.session.add(note_b)
        db.session.flush()

        quiz_b = Quiz(user_id=u2.id, note_id=note_b.id, title="Beta Quiz", engine_used="offline")
        db.session.add(quiz_b)
        db.session.flush()

        q_b = Question(
            quiz_id=quiz_b.id,
            text="Beta Question?",
            options=["W", "X", "Y", "Z"],
            correct_index=1,
            explanation="X is correct.",
            topic="BetaTopic"
        )
        db.session.add(q_b)
        db.session.flush()

        att_b = Attempt(user_id=u2.id, quiz_id=quiz_b.id, score=0, total=1)
        db.session.add(att_b)

        fc_b = Flashcard(user_id=u2.id, note_id=note_b.id, front="BetaFront", back="BetaBack", due_date=date.today())
        db.session.add(fc_b)

        db.session.commit()

        return {
            "u1_id": u1.id,
            "u2_id": u2.id,
            "note_a_id": note_a.id,
            "note_b_id": note_b.id,
            "quiz_a_id": quiz_a.id,
            "quiz_b_id": quiz_b.id,
            "att_a_id": att_a.id,
            "att_b_id": att_b.id,
            "fc_a_id": fc_a.id,
            "fc_b_id": fc_b.id,
        }
