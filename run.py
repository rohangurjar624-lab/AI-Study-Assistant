import os
from app import create_app
from app.extensions import db

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.cli.command("seed")
def seed_command():
    """Populates the database with demo account and sample study materials."""
    from seed import seed_database
    seed_database()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
