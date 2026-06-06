# 🔧 Complete Source Code Listing & Annotations

## Overview
This document contains annotated source code for all 19 Python files in the TraceNet application, organized by module.

**Note**: For complete code, refer to actual files in repository. This is a comprehensive guide with key sections.

---

## Table of Contents
1. Core Application (2 files)
2. Database Models (1 file)
3. Routes / API (7 files)
4. Utilities (5 files)
5. Configuration (1 file)

---

## Core Application Files

### 1. `app.py` - Flask Application Factory

```python
"""
Missing Person Tracking & Crime Pattern Analysis System
Main Flask Application Entry Point

This file creates the Flask application instance, initializes the database,
registers all blueprints (API routes), and seeds demo data on startup.
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

# Add base directory to Python path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from models.database import db, User
from routes.missing_persons import missing_bp
from routes.crime_data import crime_bp
from routes.ai_features import ai_bp
from routes.dashboard import dashboard_bp
from routes.notifications import notifications_bp

# Initialize Flask-Login for session management
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated
login_manager.login_message_category = 'info'


def create_app():
    """
    Application Factory Pattern
    
    Creates and configures Flask application with:
    - Database initialization
    - CORS setup
    - Blueprint registration
    - Demo data seeding
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes (allows cross-origin requests)
    CORS(app)

    # Initialize database with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register all API blueprints with URL prefixes
    app.register_blueprint(missing_bp, url_prefix='/api/missing')
    app.register_blueprint(crime_bp, url_prefix='/api/crime')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    # Register UI and authentication routes
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from routes.ui import ui_bp
    app.register_blueprint(ui_bp)

    # Context processor: inject configuration variables into templates
    @app.context_processor
    def inject_face_threshold():
        return {
            'face_match_confidence_threshold': app.config.get(
                'FACE_MATCH_CONFIDENCE_THRESHOLD', 70.0
            )
        }

    # Application context: create tables and seed data on startup
    with app.app_context():
        # Create all database tables based on model definitions
        db.create_all()
        
        # Seed sample data for demo
        from utils.seed_data import seed_crime_data, seed_missing_persons
        seed_crime_data()      # Add sample crime incidents
        seed_missing_persons()  # Add sample missing person reports

    return app


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback to load user by ID
    
    Args:
        user_id (str): User ID from session
        
    Returns:
        User: User object if exists, None otherwise
    """
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app = create_app()
    # Run development server on localhost:5000
    # Debug mode: auto-reload on code changes
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

### 2. `config.py` - Configuration Management

```python
"""
Configuration Management for TraceNet Application

Manages environment-specific settings:
- Database connections
- File upload settings
- Face recognition thresholds
- Firebase credentials
- ML model paths
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration for TraceNet application"""
    
    # ==================== Database Configuration ====================
    # SQLAlchemy database URI (MySQL or SQLite for demo)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///missing_tracker.db'  # Default: SQLite for demo
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ==================== File Upload Configuration ====================
    # Directory to store uploaded photos
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), 
        'static', 
        'uploads'
    )
    # Maximum file size: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    
    # ==================== Face Recognition Configuration ====================
    # Confidence threshold for face matching (0-100)
    # Matches with confidence > threshold are considered positive
    FACE_MATCH_CONFIDENCE_THRESHOLD = 70.0
    
    # ==================== Secret Key & Security ====================
    # Secret key for session encryption (from environment or generate)
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )
    
    # ==================== Firebase Configuration ====================
    # Firebase project configuration for push notifications
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    FIREBASE_PRIVATE_KEY_ID = os.getenv('FIREBASE_PRIVATE_KEY_ID', '')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY', '')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL', '')
    FIREBASE_CLIENT_ID = os.getenv('FIREBASE_CLIENT_ID', '')
    
    # ==================== Flask Configuration ====================
    # Session timeout in seconds (12 hours)
    PERMANENT_SESSION_LIFETIME = 12 * 60 * 60
    # JSON response settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    # Use environment database URI for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory DB for tests


# Select config based on FLASK_ENV environment variable
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## Database Models

### 3. `models/database.py` - ORM Models

```python
"""
SQLAlchemy ORM Models for TraceNet Database

Defines all database tables and relationships:
- User (authentication)
- MissingPerson (missing person reports)
- CrimeData (crime incidents)
- NotificationDevice (Firebase device tokens)
- AlertHistory (notification audit trail)
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        default='Public',
        nullable=False,
        index=True
        # Options: 'Public', 'Police', 'Admin'
    )
    created_on = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    missing_persons = db.relationship('MissingPerson', backref='reporter', lazy=True)
    crimes = db.relationship('CrimeData', backref='creator', lazy=True)
    devices = db.relationship('NotificationDevice', backref='user', lazy=True)
    
    def set_password(self, password: str) -> None:
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class MissingPerson(db.Model):
    """Missing person report model"""
    __tablename__ = 'missing_persons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    photo = db.Column(db.String(255))  # Filename stored in /static/uploads/
    last_seen = db.Column(db.String(255))  # Location description
    description = db.Column(db.Text)  # Physical description
    contact = db.Column(db.String(120))  # Reporter contact
    status = db.Column(
        db.String(20),
        default='missing',
        nullable=False,
        index=True
        # Options: 'missing', 'found'
    )
    date_reported = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<MissingPerson {self.name} ({self.status})>'


class CrimeData(db.Model):
    """Crime incident model"""
    __tablename__ = 'crime_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(120), index=True)  # e.g., Theft, Robbery, Assault
    severity = db.Column(db.Integer, default=1)  # Scale 1-5
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    lat = db.Column(db.Float)  # Latitude for geo-mapping
    lng = db.Column(db.Float)  # Longitude for geo-mapping
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<CrimeData {self.location} - {self.type} ({self.severity})>'


class NotificationDevice(db.Model):
    """Firebase device token for push notifications"""
    __tablename__ = 'notification_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    platform = db.Column(db.String(50))  # iOS, Android, Web
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_used = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<NotificationDevice {self.platform}>'


class AlertHistory(db.Model):
    """Audit trail for notifications sent"""
    __tablename__ = 'alert_history'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(100))  # e.g., face_match, risk_alert
    reference = db.Column(db.String(255))  # Related entity ID
    message = db.Column(db.Text)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    device_id = db.Column(
        db.Integer,
        db.ForeignKey('notification_devices.id'),
        nullable=True
    )
    sent_status = db.Column(
        db.String(20),
        default='pending'
        # Options: pending, sent, failed, bounced
    )
    created_on = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AlertHistory {self.alert_type}>'
```

---

## Route Modules

### 4. `routes/missing_persons.py` - Missing Person CRUD API

```python
"""
Missing Person Management API Endpoints

Provides REST API for:
- Creating missing person reports
- Retrieving person records
- Updating person status
- Deleting records
- Photo uploads with face encoding generation
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from models.database import db, MissingPerson
from config import Config
from utils.face_utils import update_face_encodings
from utils.helpers import allowed_file

missing_bp = Blueprint('missing', __name__)


@missing_bp.route('/add', methods=['POST'])
def add_missing_person():
    """
    Add a new missing person report
    
    POST /api/missing/add
    Content-Type: multipart/form-data
    
    Form Parameters:
        - name (str, required): Person's full name
        - age (int, optional): Age at report time
        - photo (file, required): Upload photo (jpg/jpeg/png, max 16MB)
        - last_seen (str, required): Location description
        - description (str, optional): Physical description
        - contact (str, required): Reporter contact info
    
    Returns:
        JSON: {
            "success": bool,
            "person_id": int,
            "message": str,
            "photo_path": str
        }
    """
    try:
        # Check if all required fields are present
        if 'name' not in request.form or 'contact' not in request.form:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'No photo file provided'}), 400
        
        # Get form data
        name = request.form.get('name')
        age = request.form.get('age', type=int)
        last_seen = request.form.get('last_seen')
        description = request.form.get('description')
        contact = request.form.get('contact')
        
        # Handle file upload
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type and size
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed: jpg, jpeg, png'
            }), 400
        
        # Save file with timestamp to avoid collisions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = secure_filename(timestamp + file.filename)
        
        # Create upload directory if not exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Create missing person record
        person = MissingPerson(
            name=name,
            age=age,
            photo=filename,
            last_seen=last_seen,
            description=description,
            contact=contact,
            status='missing',
            date_reported=datetime.utcnow()
        )
        
        db.session.add(person)
        db.session.commit()
        
        # Generate face encoding for newly uploaded photo
        try:
            update_face_encodings(person.id, filepath)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Face encoding failed for person {person.id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'person_id': person.id,
            'message': f'Missing person report {person.id} created successfully',
            'photo_path': f'/static/uploads/{filename}'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@missing_bp.route('/list', methods=['GET'])
def list_missing_persons():
    """
    Get list of all missing persons
    
    GET /api/missing/list?status=missing&limit=10&offset=0
    
    Query Parameters:
        - status (str, optional): Filter by 'missing' or 'found'
        - limit (int, optional): Results per page (default: 10)
        - offset (int, optional): Pagination offset (default: 0)
    
    Returns:
        JSON: {
            "success": bool,
            "persons": [{...}],
            "total": int,
            "limit": int,
            "offset": int
        }
    """
    try:
        status = request.args.get('status', default=None)
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Build query
        query = MissingPerson.query
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        persons = query.limit(limit).offset(offset).all()
        
        # Convert to JSON-serializable format
        persons_data = [
            {
                'id': p.id,
                'name': p.name,
                'age': p.age,
                'photo': f'/static/uploads/{p.photo}' if p.photo else None,
                'last_seen': p.last_seen,
                'status': p.status,
                'date_reported': p.date_reported.isoformat(),
                'contact': p.contact
            }
            for p in persons
        ]
        
        return jsonify({
            'success': True,
            'persons': persons_data,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@missing_bp.route('/<int:person_id>/status', methods=['PUT'])
def update_person_status(person_id):
    """
    Update missing person status (missing/found)
    
    PUT /api/missing/<person_id>/status
    
    JSON Body:
        {
            "status": "found"  // "missing" or "found"
        }
    
    Returns:
        JSON: {
            "success": bool,
            "person": {...},
            "message": str
        }
    """
    try:
        data = request.get_json()
        person = MissingPerson.query.get(person_id)
        
        if not person:
            return jsonify({'success': False, 'message': 'Person not found'}), 404
        
        new_status = data.get('status')
        if new_status not in ['missing', 'found']:
            return jsonify({
                'success': False,
                'message': 'Invalid status. Must be "missing" or "found"'
            }), 400
        
        person.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'person': {
                'id': person.id,
                'name': person.name,
                'status': person.status,
                'date_reported': person.date_reported.isoformat()
            },
            'message': f'Person status updated to {new_status}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@missing_bp.route('/<int:person_id>', methods=['GET'])
def get_person_details(person_id):
    """Get detailed information about a specific missing person"""
    try:
        person = MissingPerson.query.get(person_id)
        if not person:
            return jsonify({'success': False, 'message': 'Person not found'}), 404
        
        return jsonify({
            'success': True,
            'person': {
                'id': person.id,
                'name': person.name,
                'age': person.age,
                'photo': f'/static/uploads/{person.photo}' if person.photo else None,
                'last_seen': person.last_seen,
                'description': person.description,
                'contact': person.contact,
                'status': person.status,
                'date_reported': person.date_reported.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@missing_bp.route('/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a missing person record"""
    try:
        person = MissingPerson.query.get(person_id)
        if not person:
            return jsonify({'success': False, 'message': 'Person not found'}), 404
        
        # Delete photo file if exists
        if person.photo:
            filepath = os.path.join(Config.UPLOAD_FOLDER, person.photo)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Person record deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
```

---

## Utility Modules

### 5. `utils/face_utils.py` - Face Recognition Engine

```python
"""
Face Recognition & Encoding Utility Module

Provides facial recognition capabilities:
- DeepFace for high-accuracy embeddings
- face_recognition library as fallback
- Cosine similarity matching
- Face encoding storage/retrieval
"""

import os
import pickle
import numpy as np
from pathlib import Path

# Try to import AI libraries with graceful fallback
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("Warning: DeepFace not available. Install: pip install deepface")

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition not available. Install: pip install face-recognition")

from models.database import db, MissingPerson
from config import Config


ENCODINGS_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    'static',
    'encodings.pkl'
)


def update_face_encodings(person_id, photo_path):
    """
    Extract face encoding from photo and store for matching
    
    Uses prioritized model selection:
    1. DeepFace (Facenet512 - 512-dim vectors)
    2. face_recognition (128-dim vectors)
    3. Mock mode (returns dummy vectors)
    
    Args:
        person_id (int): Missing person ID
        photo_path (str): Path to photo file
        
    Returns:
        dict: {'success': bool, 'encoding_shape': tuple}
    """
    try:
        # Load encodings dictionary
        if os.path.exists(ENCODINGS_FILE):
            with open(ENCODINGS_FILE, 'rb') as f:
                encodings = pickle.load(f)
        else:
            encodings = {}
        
        encoding = None
        model_used = None
        
        # Try DeepFace first (most accurate)
        if DEEPFACE_AVAILABLE:
            try:
                embedding = DeepFace.represent(
                    img_path=photo_path,
                    model_name='Facenet512',
                    enforce_detection=False
                )
                if embedding and len(embedding) > 0:
                    encoding = np.array(embedding[0]['embedding'])
                    model_used = 'deepface_facenet512'
            except Exception as e:
                print(f"DeepFace error: {e}")
        
        # Fallback to face_recognition
        if encoding is None and FACE_RECOGNITION_AVAILABLE:
            try:
                image = face_recognition.load_image_file(photo_path)
                face_encodings = face_recognition.face_encodings(image)
                if len(face_encodings) > 0:
                    encoding = face_encodings[0]
                    model_used = 'face_recognition'
            except Exception as e:
                print(f"face_recognition error: {e}")
        
        # Mock mode for testing
        if encoding is None:
            print(f"Mock face encoding for person {person_id}")
            encoding = np.random.rand(128).astype(np.float64)
            model_used = 'mock'
        
        # Store encoding
        encodings[str(person_id)] = {
            'embedding': encoding.tolist(),
            'model': model_used
        }
        
        # Save to pickle file
        os.makedirs(os.path.dirname(ENCODINGS_FILE), exist_ok=True)
        with open(ENCODINGS_FILE, 'wb') as f:
            pickle.dump(encodings, f)
        
        return {
            'success': True,
            'encoding_shape': encoding.shape,
            'model': model_used
        }
        
    except Exception as e:
        print(f"Error updating face encodings: {e}")
        return {'success': False, 'error': str(e)}


def find_matching_person(query_photo_path, confidence_threshold=70.0):
    """
    Find matching missing persons for a query photo
    
    Args:
        query_photo_path (str): Path to query image
        confidence_threshold (float): Confidence % threshold (default 70)
        
    Returns:
        list: Matches sorted by confidence descending
        [
            {
                'person_id': int,
                'name': str,
                'confidence': float (0-100),
                'age': int,
                'last_seen': str,
                'photo': str,
                'status': str
            },
            ...
        ]
    """
    try:
        # Extract query encoding
        query_encoding = None
        
        if DEEPFACE_AVAILABLE:
            try:
                embedding = DeepFace.represent(
                    img_path=query_photo_path,
                    model_name='Facenet512',
                    enforce_detection=False
                )
                if embedding:
                    query_encoding = np.array(embedding[0]['embedding'])
            except Exception as e:
                print(f"DeepFace query error: {e}")
        
        if query_encoding is None and FACE_RECOGNITION_AVAILABLE:
            try:
                image = face_recognition.load_image_file(query_photo_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    query_encoding = encodings[0]
            except Exception as e:
                print(f"face_recognition query error: {e}")
        
        if query_encoding is None:
            return {'success': False, 'matches': []}
        
        # Load stored encodings
        if not os.path.exists(ENCODINGS_FILE):
            return {'success': True, 'matches': []}
        
        with open(ENCODINGS_FILE, 'rb') as f:
            encodings = pickle.load(f)
        
        # Compute similarity with all stored encodings
        matches = []
        
        for person_id_str, encoding_data in encodings.items():
            person_id = int(person_id_str)
            stored_encoding = np.array(encoding_data['embedding'])
            
            # Cosine similarity
            similarity = np.dot(query_encoding, stored_encoding) / (
                np.linalg.norm(query_encoding) * np.linalg.norm(stored_encoding)
            )
            confidence = max(0, min(100, similarity * 100))  # Scale to 0-100
            
            if confidence >= confidence_threshold:
                # Get person details
                person = MissingPerson.query.get(person_id)
                if person:
                    matches.append({
                        'person_id': person_id,
                        'name': person.name,
                        'confidence': round(confidence, 2),
                        'age': person.age,
                        'last_seen': person.last_seen,
                        'photo': f'/static/uploads/{person.photo}' if person.photo else None,
                        'status': person.status
                    })
        
        # Sort by confidence descending
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {'success': True, 'matches': matches}
        
    except Exception as e:
        print(f"Error finding matches: {e}")
        return {'success': False, 'error': str(e), 'matches': []}


def rebuild_all_encodings():
    """
    Regenerate all face encodings from stored photos
    Useful when switching models or updating encodings
    
    Returns:
        dict: {'success': bool, 'processed': int, 'failed': int}
    """
    try:
        persons = MissingPerson.query.all()
        processed = 0
        failed = 0
        
        for person in persons:
            if person.photo:
                filepath = os.path.join(Config.UPLOAD_FOLDER, person.photo)
                if os.path.exists(filepath):
                    result = update_face_encodings(person.id, filepath)
                    if result['success']:
                        processed += 1
                    else:
                        failed += 1
        
        return {
            'success': True,
            'processed': processed,
            'failed': failed,
            'message': f'Rebuilt {processed} encodings, {failed} failed'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

## Remaining Documentation

Due to space limitations, here's a summary of remaining modules:

### 6-10. Other Route Files
- **routes/crime_data.py**: Crime incident CRUD + statistics
- **routes/ai_features.py**: Face matching & risk prediction endpoints
- **routes/dashboard.py**: Analytics & summary data
- **routes/auth.py**: User login/signup/logout
- **routes/notifications.py**: Firebase device token management

### 11-15. Utility Files
- **utils/ml_utils.py**: Random Forest crime prediction
- **utils/firebase_utils.py**: FCM push notifications
- **utils/helpers.py**: File validation utilities
- **utils/seed_data.py**: Demo data generation
- **routes/ui.py**: HTML template routes

### 16-19. Additional Files
- **config.py**: Configuration management
- **models/database.py**: SQLAlchemy ORM models
- **.env.example**: Environment variables template
- **requirements.txt**: Python dependencies

---

## Key Code Patterns Used

### 1. Factory Pattern (app.py)
```python
def create_app():
    app = Flask(__name__)
    # Configure and return app instance
    return app
```

### 2. Blueprint Pattern (routes)
```python
missing_bp = Blueprint('missing', __name__)

@missing_bp.route('/add', methods=['POST'])
def add_missing_person():
    pass

app.register_blueprint(missing_bp, url_prefix='/api/missing')
```

### 3. ORM Model Pattern (models)
```python
class MissingPerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
```

### 4. Error Handling Pattern
```python
try:
    # Attempt operation
    result = do_something()
    return jsonify({'success': True, 'data': result}), 200
except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'message': str(e)}), 500
```

---

**For complete source code with all comments, refer to actual repository files.**

