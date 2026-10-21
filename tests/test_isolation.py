def test_user_cannot_access_other_users_note(client, two_users):
    # Log in as user_alpha
    client.post("/auth/login", data={"email": "alpha@example.com", "password": "password123"}, follow_redirects=True)

    # Note B belongs to user_beta
    note_b_id = two_users["note_b_id"]

    # 1. View Note B -> 404
    res_view = client.get(f"/notes/{note_b_id}")
    assert res_view.status_code == 404

    # 2. Edit Note B -> 404
    res_edit = client.get(f"/notes/{note_b_id}/edit")
    assert res_edit.status_code == 404

    res_edit_post = client.post(f"/notes/{note_b_id}/edit", data={"title": "Hacked", "content": "Hacked text " * 20})
    assert res_edit_post.status_code == 404

    # 3. Delete Note B -> 404
    res_del = client.post(f"/notes/{note_b_id}/delete")
    assert res_del.status_code == 404

    # 4. Regenerate Note B -> 404
    res_regen = client.post(f"/notes/{note_b_id}/regenerate")
    assert res_regen.status_code == 404

    # 5. Create Quiz from Note B -> 404
    res_quiz_new = client.post(f"/notes/{note_b_id}/quiz/new", data={"count": "5"})
    assert res_quiz_new.status_code == 404

    # 6. Create Flashcards from Note B -> 404
    res_fc_new = client.post(f"/notes/{note_b_id}/flashcards/new", data={"count": "5"})
    assert res_fc_new.status_code == 404


def test_user_cannot_access_other_users_quiz(client, two_users):
    # Log in as user_alpha
    client.post("/auth/login", data={"email": "alpha@example.com", "password": "password123"}, follow_redirects=True)

    quiz_b_id = two_users["quiz_b_id"]

    # Take Quiz B -> 404
    res_take_get = client.get(f"/quiz/{quiz_b_id}")
    assert res_take_get.status_code == 404

    res_take_post = client.post(f"/quiz/{quiz_b_id}", data={"duration_seconds": "10"})
    assert res_take_post.status_code == 404


def test_user_cannot_access_other_users_attempt(client, two_users):
    # Log in as user_alpha
    client.post("/auth/login", data={"email": "alpha@example.com", "password": "password123"}, follow_redirects=True)

    att_b_id = two_users["att_b_id"]

    # View Attempt B -> 404
    res_att = client.get(f"/quiz/attempt/{att_b_id}")
    assert res_att.status_code == 404


def test_user_cannot_grade_other_users_flashcard(client, two_users):
    # Log in as user_alpha
    client.post("/auth/login", data={"email": "alpha@example.com", "password": "password123"}, follow_redirects=True)

    fc_b_id = two_users["fc_b_id"]

    # Grade Flashcard B -> 404
    res_grade = client.post("/flashcards/review", data={"card_id": str(fc_b_id), "grade": "5"})
    assert res_grade.status_code == 404
