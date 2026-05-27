"""
Configuration settings for the Missing Person Tracking System
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'missing-tracker-secret-2024')

    # ── Database ──────────────────────────────────────────────────────────────
    # SQLite for development. Change to MySQL for production.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///missing_tracker.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # ── Face Recognition ──────────────────────────────────────────────────────
    FACE_MATCH_THRESHOLD = 0.6   # Internal face distance threshold used for score mapping
    FACE_MATCH_CONFIDENCE_THRESHOLD = 70.0  # Minimum match percent to consider a true match
    FACE_ENCODINGS_FILE = os.path.join(BASE_DIR, 'utils', 'face_encodings.pkl')

    # ── ML Model ──────────────────────────────────────────────────────────────
    MODEL_FILE = os.path.join(BASE_DIR, 'utils', 'crime_model.pkl')

    # ── Firebase Notifications ─────────────────────────────────────────────────
    FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY', '')
    CRIME_ALERT_PROBABILITY_THRESHOLD = float(os.environ.get('CRIME_ALERT_PROBABILITY_THRESHOLD', '70.0'))
    NOTIFICATION_ALERT_WINDOW_HOURS = int(os.environ.get('NOTIFICATION_ALERT_WINDOW_HOURS', '6'))

    # ── Firebase Web Push ─────────────────────────────────────────────────────
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '')
    FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID', '')
    FIREBASE_VAPID_KEY = os.environ.get('FIREBASE_VAPID_KEY', '')
