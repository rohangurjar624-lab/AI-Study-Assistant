from app.models import Note, Quiz, Question, Attempt
from app.extensions import db


SAMPLE_CONTENT = (
    "Photosynthesis is a vital biological mechanism utilized by plants, algae, and certain bacteria. "
    "Through sunlight absorption by chlorophyll pigments within chloroplast thylakoids, light reactions "
    "produce chemical energy in the form of ATP and NADPH. These energy carriers subsequently enter the Calvin cycle "
    "in the stroma, where the enzyme RuBisCO fixes atmospheric carbon dioxide into high-energy sugars."
)


def test_generate_quiz_from_note(auth_client, app, auth_user):
    with app.app_context():
        note = Note(
            title="Genetics Notes",
            content=SAMPLE_CONTENT,
            source_type="paste",
            user_id=auth_user,
        )
        db.session.add(note)
        db.session.commit()
        note_id = note.id

    res = auth_client.post(
        f"/notes/{note_id}/quiz/new",
        data={"count": "5"},
        follow_redirects=True,
    )
    assert res.status_code == 200

    with app.app_context():
        quiz = Quiz.query.filter_by(note_id=note_id).first()
        assert quiz is not None
        assert len(quiz.questions) == 5


def test_correct_answers_absent_from_quiz_html(auth_client, app, auth_user):
    with app.app_context():
        note = Note(title="Secret Quiz Note", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(note)
        db.session.commit()

        quiz = Quiz(title="Security Assessment", user_id=auth_user, note_id=note.id)
        db.session.add(quiz)
        db.session.flush()

        secret_explanation = "ThisSuperSecretExplanationMustNeverLeakInHtmlBeforeSubmission"
        q = Question(
            quiz_id=quiz.id,
            text="Which organelle houses chlorophyll?",
            options=["Mitochondria", "Chloroplast", "Golgi apparatus", "Ribosome"],
            correct_index=1,
            explanation=secret_explanation,
            topic="Plant Cell",
        )
        db.session.add(q)
        db.session.commit()
        quiz_id = quiz.id

    # GET quiz taking page
    res = auth_client.get(f"/quiz/{quiz_id}")
    assert res.status_code == 200

    # Ensure question text and options are present
    assert b"Which organelle houses chlorophyll?" in res.data
    assert b"Chloroplast" in res.data
    assert b"Mitochondria" in res.data

    # CRITICAL SECURITY CHECK:
    # Neither correct_index nor explanation should appear in the HTML
    assert secret_explanation.encode("utf-8") not in res.data
    assert b"correct_index" not in res.data
    assert b"correct-index" not in res.data


def test_quiz_scoring_all_correct(auth_client, app, auth_user):
    with app.app_context():
        note = Note(title="Scoring Note", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(note)
        db.session.commit()

        quiz = Quiz(title="Perfect Score Quiz", user_id=auth_user, note_id=note.id)
        db.session.add(quiz)
        db.session.flush()

        q1 = Question(quiz_id=quiz.id, text="Q1", options=["A", "B", "C", "D"], correct_index=0, explanation="E1")
        q2 = Question(quiz_id=quiz.id, text="Q2", options=["A", "B", "C", "D"], correct_index=2, explanation="E2")
        db.session.add_all([q1, q2])
        db.session.commit()
        quiz_id = quiz.id
        q1_id = q1.id
        q2_id = q2.id

    # Submit all correct answers
    res = auth_client.post(
        f"/quiz/{quiz_id}",
        data={
            f"q_{q1_id}": "0",
            f"q_{q2_id}": "2",
            "duration_seconds": "45",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"2 / 2" in res.data
    assert b"100.0%" in res.data
    assert b"E1" in res.data
    assert b"E2" in res.data


def test_quiz_scoring_partial_and_unanswered(auth_client, app, auth_user):
    with app.app_context():
        note = Note(title="Partial Note", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(note)
        db.session.commit()

        quiz = Quiz(title="Partial Score Quiz", user_id=auth_user, note_id=note.id)
        db.session.add(quiz)
        db.session.flush()

        q1 = Question(quiz_id=quiz.id, text="Q1", options=["A", "B", "C", "D"], correct_index=0, explanation="E1")
        q2 = Question(quiz_id=quiz.id, text="Q2", options=["A", "B", "C", "D"], correct_index=1, explanation="E2")
        q3 = Question(quiz_id=quiz.id, text="Q3", options=["A", "B", "C", "D"], correct_index=2, explanation="E3")
        db.session.add_all([q1, q2, q3])
        db.session.commit()
        quiz_id = quiz.id
        q1_id = q1.id
        q2_id = q2.id
        q3_id = q3.id

    # Q1: correct (0), Q2: wrong (3), Q3: unanswered
    res = auth_client.post(
        f"/quiz/{quiz_id}",
        data={
            f"q_{q1_id}": "0",
            f"q_{q2_id}": "3",
            # q3 omitted
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"1 / 3" in res.data
    assert b"33.3%" in res.data
    assert b"No answer selected" in res.data


def test_quiz_scoring_tampered_index_rejected(auth_client, app, auth_user):
    with app.app_context():
        note = Note(title="Tamper Note", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(note)
        db.session.commit()

        quiz = Quiz(title="Tamper Quiz", user_id=auth_user, note_id=note.id)
        db.session.add(quiz)
        db.session.flush()

        q1 = Question(quiz_id=quiz.id, text="Q1", options=["A", "B", "C", "D"], correct_index=0, explanation="E1")
        db.session.add(q1)
        db.session.commit()
        quiz_id = quiz.id
        q1_id = q1.id

    # Submit out of range index 999 and negative index
    res = auth_client.post(
        f"/quiz/{quiz_id}",
        data={f"q_{q1_id}": "999"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"0 / 1" in res.data
