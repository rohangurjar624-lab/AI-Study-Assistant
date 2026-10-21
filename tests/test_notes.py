import io
from app.models import Note
from app.extensions import db


SAMPLE_CONTENT = (
    "Photosynthesis is a vital biological mechanism utilized by plants, algae, and certain bacteria. "
    "Through sunlight absorption by chlorophyll pigments within chloroplast thylakoids, light reactions "
    "produce chemical energy in the form of ATP and NADPH. These energy carriers subsequently enter the Calvin cycle "
    "in the stroma, where the enzyme RuBisCO fixes atmospheric carbon dioxide into high-energy sugars."
)


def test_create_note_via_paste(auth_client, app):
    res = auth_client.post(
        "/notes/new",
        data={
            "title": "Bio Chapter 1",
            "content": SAMPLE_CONTENT,
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Note created and analyzed successfully!" in res.data

    with app.app_context():
        note = Note.query.filter_by(title="Bio Chapter 1").first()
        assert note is not None
        assert note.source_type == "paste"
        assert note.summary is not None
        assert len(note.keywords) > 0


def test_create_note_via_txt_upload(auth_client, app):
    data = {
        "title": "Uploaded Notes",
        "file": (io.BytesIO(SAMPLE_CONTENT.encode("utf-8")), "cell_bio.txt"),
    }
    res = auth_client.post(
        "/notes/new",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Uploaded Notes" in res.data

    with app.app_context():
        note = Note.query.filter_by(title="Uploaded Notes").first()
        assert note is not None
        assert note.source_type == "txt"
        assert note.original_filename == "cell_bio.txt"


def test_notes_search_and_pagination(auth_client, app, auth_user):
    with app.app_context():
        for i in range(15):
            n = Note(
                title=f"Physics Part {i+1}",
                content=SAMPLE_CONTENT,
                source_type="paste",
                user_id=auth_user,
            )
            db.session.add(n)
        db.session.commit()

    # Default page 1: should show 10 items
    res = auth_client.get("/notes")
    assert res.status_code == 200
    assert b"Physics Part 15" in res.data
    assert b"Page 1 of 2" in res.data

    # Page 2: should show remaining 5
    res2 = auth_client.get("/notes?page=2")
    assert res2.status_code == 200
    assert b"Page 2 of 2" in res2.data

    # Search filter
    res_search = auth_client.get("/notes?q=Part 14")
    assert res_search.status_code == 200
    assert b"Physics Part 14" in res_search.data
    assert b"Physics Part 12" not in res_search.data


def test_edit_note(auth_client, app, auth_user):
    with app.app_context():
        n = Note(
            title="Original Title",
            content=SAMPLE_CONTENT,
            source_type="paste",
            user_id=auth_user,
        )
        db.session.add(n)
        db.session.commit()
        note_id = n.id

    res = auth_client.post(
        f"/notes/{note_id}/edit",
        data={
            "title": "Updated Title",
            "content": SAMPLE_CONTENT + " Additional text to keep length valid.",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Note updated successfully" in res.data

    with app.app_context():
        updated = db.session.get(Note, note_id)
        assert updated.title == "Updated Title"


def test_delete_note_cascades(auth_client, app, auth_user):
    with app.app_context():
        n = Note(
            title="Delete Me",
            content=SAMPLE_CONTENT,
            source_type="paste",
            user_id=auth_user,
        )
        db.session.add(n)
        db.session.commit()
        nid = n.id

    res = auth_client.post(f"/notes/{nid}/delete", follow_redirects=True)
    assert res.status_code == 200
    assert b"deleted" in res.data

    with app.app_context():
        assert db.session.get(Note, nid) is None


def test_regenerate_note(auth_client, app, auth_user):
    with app.app_context():
        n = Note(
            title="Regenerate Me",
            content=SAMPLE_CONTENT,
            source_type="paste",
            user_id=auth_user,
            summary="Old summary",
            keywords=["Old"],
        )
        db.session.add(n)
        db.session.commit()
        nid = n.id

    res = auth_client.post(f"/notes/{nid}/regenerate", follow_redirects=True)
    assert res.status_code == 200
    assert b"re-generated successfully" in res.data

    with app.app_context():
        refreshed = db.session.get(Note, nid)
        assert refreshed.summary != "Old summary"
