from urllib.parse import urlsplit
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db, limiter
from app.models import User
from app.forms import RegisterForm, LoginForm, EmptyForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_redirect(target: str) -> bool:
    """Ensures target is a safe relative URL starting with / and not //."""
    if not target:
        return False
    # Must start with single / and not // (protocol-relative URLs)
    if not target.startswith("/") or target.startswith("//"):
        return False
    parsed = urlsplit(target)
    # Target should not have host or scheme
    return not parsed.netloc and not parsed.scheme


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5/minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        clean_email = form.email.data.strip().lower()
        clean_username = form.username.data.strip()

        # Check existing user
        if User.query.filter_by(username=clean_username).first():
            flash("Username is already taken. Please choose another.", "danger")
            return render_template("auth/register.html", form=form)

        if User.query.filter_by(email=clean_email).first():
            flash("An account with that email already exists. Please log in.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            username=clean_username,
            email=clean_email,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10/minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        clean_email = form.email.data.strip().lower()
        user = User.query.filter_by(email=clean_email).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        login_user(user, remember=form.remember_me.data)
        flash(f"Welcome back, {user.username}!", "success")

        next_page = request.args.get("next")
        if next_page and is_safe_redirect(next_page):
            return redirect(next_page)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    form = EmptyForm()
    if form.validate_on_submit():
        logout_user()
        flash("You have been signed out.", "info")
    return redirect(url_for("home"))
