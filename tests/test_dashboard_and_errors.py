from app.models import User
from app.extensions import db


def test_dashboard_renders(auth_client):
    res = auth_client.get("/dashboard")
    assert res.status_code == 200
    assert b"Learning Progress & Analytics" in res.data
    assert b"Total Notes" in res.data


def test_dashboard_data_endpoint(auth_client):
    res = auth_client.get("/dashboard/data")
    assert res.status_code == 200
    json_data = res.get_json()
    assert "chart1" in json_data
    assert "chart2" in json_data
    assert "labels" in json_data["chart1"]
    assert "scores" in json_data["chart1"]


def test_profile_update_username(auth_client, app, auth_user):
    res = auth_client.post(
        "/profile",
        data={
            "form_action": "change_username",
            "user-username": "updated_uname",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Username updated successfully" in res.data

    with app.app_context():
        user = db.session.get(User, auth_user)
        assert user.username == "updated_uname"


def test_profile_update_password(auth_client, app, auth_user):
    res = auth_client.post(
        "/profile",
        data={
            "form_action": "change_password",
            "pass-current_password": "password123",
            "pass-new_password": "newSecurePassword123",
            "pass-confirm_new_password": "newSecurePassword123",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Password updated successfully" in res.data

    with app.app_context():
        user = db.session.get(User, auth_user)
        assert user.check_password("newSecurePassword123")


def test_profile_delete_account(auth_client, app, auth_user):
    res = auth_client.post(
        "/profile",
        data={
            "form_action": "delete_account",
            "del-confirm_username": "testuser",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"permanently deleted" in res.data

    with app.app_context():
        assert db.session.get(User, auth_user) is None


def test_demo_account_protected(client, app):
    with app.app_context():
        demo_u = User(username="demo", email="demo@example.com")
        demo_u.set_password("DemoPass123!")
        db.session.add(demo_u)
        db.session.commit()

    # Log in as demo
    client.post("/auth/login", data={"email": "demo@example.com", "password": "DemoPass123!"}, follow_redirects=True)

    # Attempt to change password
    res_pass = client.post(
        "/profile",
        data={
            "form_action": "change_password",
            "pass-current_password": "DemoPass123!",
            "pass-new_password": "NewDemoPassword123!",
            "pass-confirm_new_password": "NewDemoPassword123!",
        },
        follow_redirects=True,
    )
    assert b"Demo account password cannot be modified" in res_pass.data

    # Attempt to delete account
    res_del = client.post(
        "/profile",
        data={
            "form_action": "delete_account",
            "del-confirm_username": "demo",
        },
        follow_redirects=True,
    )
    assert b"The demo account cannot be deleted" in res_del.data


def test_custom_404_page(client):
    res = client.get("/nonexistent-endpoint-abc")
    assert res.status_code == 404
    assert b"404 - Page Not Found" in res.data


def test_healthz_endpoint(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.data == b"ok"
