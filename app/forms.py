from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField,
    HiddenField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional,
    NumberRange,
    Regexp,
)


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50, message="Username must be between 3 and 50 characters."),
            Regexp(r"^[A-Za-z0-9_.-]+$", message="Username may only contain letters, numbers, underscores, and dashes.")
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address."),
            Length(max=120)
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long.")
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(message="Please enter a valid email address.")],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Sign In")


class NoteForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required."),
            Length(max=120, message="Title cannot exceed 120 characters.")
        ],
    )
    content = TextAreaField(
        "Paste Notes (at least 200 characters)",
        validators=[Optional(), Length(max=50000, message="Content cannot exceed 50,000 characters.")],
    )
    file = FileField(
        "Or Upload Document (.txt or .pdf, max 5 MB)",
        validators=[Optional(), FileAllowed(["txt", "pdf"], "Only .txt and .pdf files are supported.")],
    )
    submit = SubmitField("Save & Analyze Note")


class QuizGenerateForm(FlaskForm):
    count = SelectField(
        "Number of Questions",
        choices=[("5", "5 Questions"), ("10", "10 Questions")],
        default="5"
    )
    submit = SubmitField("Generate Quiz")


class FlashcardGenerateForm(FlaskForm):
    count = SelectField(
        "Number of Cards",
        choices=[("5", "5 Cards"), ("10", "10 Cards"), ("15", "15 Cards")],
        default="10"
    )
    submit = SubmitField("Generate Flashcards")


class CardReviewForm(FlaskForm):
    card_id = HiddenField("Card ID", validators=[DataRequired()])
    grade = IntegerField("Grade", validators=[DataRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField("Submit Grade")


class ChangeUsernameForm(FlaskForm):
    username = StringField(
        "New Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50, message="Username must be between 3 and 50 characters."),
            Regexp(r"^[A-Za-z0-9_.-]+$", message="Username may only contain letters, numbers, underscores, and dashes.")
        ],
    )
    submit = SubmitField("Change Username")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long.")
        ],
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match.")
        ],
    )
    submit = SubmitField("Change Password")


class DeleteAccountForm(FlaskForm):
    confirm_username = StringField("Type your username to confirm", validators=[DataRequired()])
    submit = SubmitField("Delete Account Permanently")


class EmptyForm(FlaskForm):
    """Empty form used exclusively for CSRF-protected POST actions."""
    pass
