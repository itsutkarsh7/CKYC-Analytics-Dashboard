from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def create_app():
    """
    Flask Application Factory
    """

    app = Flask(__name__)

    # Load Configuration
    app.config.from_object("config.Config")

    # Initialize Database
    db.init_app(app)

    # -------------------------
    # Register Blueprints
    # -------------------------
    from app.routes.dashboard import dashboard_bp
    from app.routes.upload import upload_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)

    # -------------------------
    # Create Database Tables
    # -------------------------
    with app.app_context():
        db.create_all()

    return app