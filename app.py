"""
Missing Person Tracking & Crime Pattern Analysis System
Main Flask Application Entry Point
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config
from models.database import db, User
from routes.missing_persons import missing_bp
from routes.crime_data import crime_bp
from routes.ai_features import ai_bp
from routes.dashboard import dashboard_bp
from routes.notifications import notifications_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # type: ignore[attr-defined]
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app)

    # Initialize database
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(missing_bp, url_prefix='/api/missing')
    app.register_blueprint(crime_bp, url_prefix='/api/crime')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Import and register the main UI routes
    from routes.ui import ui_bp
    app.register_blueprint(ui_bp)

    @app.context_processor
    def inject_face_threshold():
        return {
            'face_match_confidence_threshold': app.config.get('FACE_MATCH_CONFIDENCE_THRESHOLD', 70.0)
        }

    # Create DB tables if they don't exist
    with app.app_context():
        db.create_all()
        # Seed some sample crime data for demo
        from utils.seed_data import seed_crime_data, seed_missing_persons
        seed_crime_data()
        seed_missing_persons()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
