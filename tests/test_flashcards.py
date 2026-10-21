from datetime import date, timedelta
from app.models import Note, Flashcard, User
from app.extensions import db


SAMPLE_CONTENT = (
    "Photosynthesis is a vital biological mechanism utilized by plants, algae, and certain bacteria. "
    "Through sunlight absorption by chlorophyll pigments within chloroplast thylakoids, light reactions "
    "produce chemical energy in the form of ATP and NADPH. These energy carriers subsequently enter the Calvin cycle "
    "in the stroma, where the enzyme RuBisCO fixes atmospheric carbon dioxide into high-energy sugars."
)


def test_create_flashcards_from_note(auth_client, app, auth_user):
    with app.app_context():
        n = Note(title="Plant Biology", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(n)
        db.session.commit()
        nid = n.id

    res = auth_client.post(
        f"/notes/{nid}/flashcards/new",
        data={"count": "5"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"flashcards" in res.data

    with app.app_context():
        cards = Flashcard.query.filter_by(note_id=nid).all()
        assert len(cards) == 5
        assert all(c.due_date == date.today() for c in cards)


def test_flashcard_review_flow_and_streak(auth_client, app, auth_user):
    today = date.today()
    with app.app_context():
        n = Note(title="Anatomy", content=SAMPLE_CONTENT, source_type="paste", user_id=auth_user)
        db.session.add(n)
        db.session.commit()

        fc = Flashcard(
            user_id=auth_user,
            note_id=n.id,
            front="Mitochondria",
            back="Powerhouse of the eukaryotic cell.",
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=today,
        )
        db.session.add(fc)
        db.session.commit()
        fc_id = fc.id

    # GET review page
    res_get = auth_client.get("/flashcards/review")
    assert res_get.status_code == 200
    assert b"Mitochondria" in res_get.data

    # POST grade 5 (perfect recall)
    res_post = auth_client.post(
        "/flashcards/review",
        data={"card_id": str(fc_id), "grade": "5"},
        follow_redirects=True,
    )
    assert res_post.status_code == 200

    with app.app_context():
        updated_card = db.session.get(Flashcard, fc_id)
        assert updated_card.repetitions == 1
        assert updated_card.interval_days == 1
        assert updated_card.due_date == today + timedelta(days=1)

        user = db.session.get(User, auth_user)
        assert user.streak_count >= 1
        assert user.last_study_date == today
