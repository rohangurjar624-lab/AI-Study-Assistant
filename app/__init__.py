from flask import Flask, render_template

from config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models  # noqa: F401  (tables ko register karta hai)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("index.html")

    return app