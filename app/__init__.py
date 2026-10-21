import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required, logout_user
from config import config
from app.extensions import db, migrate, login_manager, csrf, limiter
from app.models import User
from app.forms import ChangeUsernameForm, ChangePasswordForm, DeleteAccountForm, EmptyForm
from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in type(dbapi_connection).__module__:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()



def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app_config = config.get(config_name, config["default"])
    if isinstance(app_config, type):
        app.config.from_object(app_config)
    else:
        app.config.from_object(app_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "info"
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.auth import auth_bp
    from app.notes import notes_bp
    from app.quiz import quiz_bp
    from app.flashcards import flashcards_bp
    from app.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(dashboard_bp)

    # Core Routes
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard"))
        return render_template("index.html")

    @app.route("/healthz")
    def healthz():
        return "ok", 200

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        is_demo = current_user.email == "demo@example.com" or current_user.username == "demo"
        username_form = ChangeUsernameForm(prefix="user")
        password_form = ChangePasswordForm(prefix="pass")
        delete_form = DeleteAccountForm(prefix="del")
        empty_form = EmptyForm()

        action = request.form.get("form_action")

        if request.method == "POST":
            if action == "change_username":
                if username_form.validate_on_submit():
                    new_uname = username_form.username.data.strip()
                    if is_demo:
                        flash("Demo account username cannot be changed.", "warning")
                    elif User.query.filter(User.username == new_uname, User.id != current_user.id).first():
                        flash("Username is already taken by another student.", "danger")
                    else:
                        current_user.username = new_uname
                        db.session.commit()
                        flash("Username updated successfully!", "success")
                    return redirect(url_for("profile"))

            elif action == "change_password":
                if is_demo:
                    flash("Demo account password cannot be modified.", "warning")
                    return redirect(url_for("profile"))
                if password_form.validate_on_submit():
                    if not current_user.check_password(password_form.current_password.data):
                        flash("Current password is incorrect.", "danger")
                    else:
                        current_user.set_password(password_form.new_password.data)
                        db.session.commit()
                        flash("Password updated successfully!", "success")
                    return redirect(url_for("profile"))

            elif action == "delete_account":
                if is_demo:
                    flash("The demo account cannot be deleted.", "warning")
                    return redirect(url_for("profile"))
                if delete_form.validate_on_submit():
                    confirm_name = delete_form.confirm_username.data.strip()
                    if confirm_name != current_user.username:
                        flash("Entered username does not match. Account deletion cancelled.", "danger")
                    else:
                        user = current_user._get_current_object()
                        logout_user()
                        db.session.delete(user)
                        db.session.commit()
                        flash("Your account and all associated data have been permanently deleted.", "info")
                        return redirect(url_for("home"))

        return render_template(
            "profile.html",
            username_form=username_form,
            password_form=password_form,
            delete_form=delete_form,
            empty_form=empty_form,
            is_demo=is_demo
        )

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp
        return response

    # Custom Error Pages
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def ratelimit_exceeded(error):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
