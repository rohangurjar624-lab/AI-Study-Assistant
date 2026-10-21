from app.models import User
from app.extensions import db


def test_registration_success(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password": "validPassword123",
            "confirm_password": "validPassword123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    with app.app_context():
        user = User.query.filter_by(username="newstudent").first()
        assert user is not None
        assert user.email == "newstudent@example.com"
        assert user.check_password("validPassword123")


def test_registration_validation_short_password(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "shortpass_user",
            "email": "short@example.com",
            "password": "short",
            "confirm_password": "short",
        },
    )
    assert response.status_code == 200
    assert b"at least 8 characters" in response.data


def test_registration_duplicate_username(client, auth_user):
    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",  # Already exists from fixture
            "email": "another@example.com",
            "password": "validPassword123",
            "confirm_password": "validPassword123",
        },
    )
    assert response.status_code == 200
    assert b"Username is already taken" in response.data


def test_registration_duplicate_email(client, auth_user):
    response = client.post(
        "/auth/register",
        data={
            "username": "distinct_user",
            "email": "TEST@example.com",  # Duplicate (stored lowercase)
            "password": "validPassword123",
            "confirm_password": "validPassword123",
        },
    )
    assert response.status_code == 200
    assert b"account with that email already exists" in response.data


def test_login_success(client, auth_user):
    response = client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back, testuser!" in response.data


def test_login_case_insensitive_email(client, auth_user):
    response = client.post(
        "/auth/login",
        data={"email": "TEST@EXAMPLE.COM", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back, testuser!" in response.data


def test_login_invalid_password_generic_error(client, auth_user):
    response = client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_invalid_email_generic_error(client):
    response = client.post(
        "/auth/login",
        data={"email": "nonexistent@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_safe_next_redirect(client, auth_user):
    response = client.post(
        "/auth/login?next=/notes",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/notes")


def test_login_open_redirect_prevented(client, auth_user):
    # Should not redirect to external site //evil.com
    response = client.post(
        "/auth/login?next=//evil.com",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    # Falls back to dashboard
    assert response.headers["Location"].endswith("/dashboard")


def test_logout_post_required(client, auth_client):
    # GET on logout should not be allowed (405 Method Not Allowed)
    get_res = client.get("/auth/logout")
    assert get_res.status_code == 405

    # POST logs out
    post_res = client.post("/auth/logout", follow_redirects=True)
    assert post_res.status_code == 200
    assert b"You have been signed out" in post_res.data


def test_protected_routes_redirect_to_login(client):
    protected_urls = ["/dashboard", "/notes", "/notes/new", "/quizzes", "/flashcards", "/profile"]
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]
