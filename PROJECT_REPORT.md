# 📋 TraceNet: Missing Person Tracking & Crime Pattern Analysis System
## Comprehensive Project Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Feature Description](#feature-description)
6. [Database Schema](#database-schema)
7. [Module Documentation](#module-documentation)
8. [API Documentation](#api-documentation)
9. [Installation & Setup](#installation--setup)
10. [Usage Guide](#usage-guide)
11. [Future Enhancements](#future-enhancements)

---

## Executive Summary

**TraceNet** is an AI-powered web application designed to assist law enforcement and the public in tracking missing persons and analyzing crime patterns. The system leverages cutting-edge technologies including:

- **Facial Recognition AI** for automated matching of missing person photos
- **Machine Learning** (Random Forest) for predicting crime hotspots and risk areas
- **Real-time Push Notifications** via Firebase Cloud Messaging
- **Role-Based Access Control** (Public/Police/Admin) for secure multi-stakeholder access

The application is built as a full-stack **Flask web application** with a **MySQL database**, **OpenCV** for computer vision, and **scikit-learn** for ML predictions. It provides a dark-themed, responsive dashboard for law enforcement agencies to manage missing persons reports and analyze crime intelligence.

---

## Project Overview

### Purpose
Provide an integrated platform for:
- ✅ Reporting missing persons with photo evidence
- ✅ Searching for missing persons using AI-powered facial recognition
- ✅ Tracking and analyzing crime incidents by location and type
- ✅ Predicting high-crime areas using machine learning
- ✅ Sending real-time alerts to stakeholders
- ✅ Enabling role-based access for different user types

### Key Objectives
1. **Reduce search time** through automated facial matching
2. **Identify crime patterns** to allocate police resources effectively
3. **Engage the public** in missing persons cases via notifications
4. **Provide actionable intelligence** through ML-driven risk predictions
5. **Maintain data security** with role-based access controls

### Project Statistics
- **Total Python Files**: 19
- **API Endpoints**: 30+
- **Database Tables**: 5
- **HTML Templates**: 11
- **AI Models Used**: DeepFace, face_recognition, scikit-learn Random Forest

---

## Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Flask | 3.0.0 |
| ORM | SQLAlchemy | 2.0.0+ |
| Database | MySQL 8.0+ / SQLite (demo) | 8.0+ |
| Python | Python | 3.9 - 3.11 |
| Security | Werkzeug (hashing) | 3.0.1 |
| CORS | Flask-CORS | 4.0.0 |

### AI & Machine Learning
| Component | Library | Purpose |
|-----------|---------|---------|
| Facial Recognition | DeepFace | Primary face matching (Facenet512 model) |
| Face Encoding Backup | face_recognition | Fallback face matching |
| Machine Learning | scikit-learn | Crime risk prediction (Random Forest) |
| Computer Vision | OpenCV | Image processing |
| Numerical Computing | NumPy | Array operations |
| Image Processing | Pillow | Photo resizing/handling |

### Frontend & Notifications
| Component | Technology |
|-----------|-----------|
| Template Engine | Jinja2 |
| CSS Framework | Bootstrap 5 / Custom CSS |
| Notifications | Firebase Cloud Messaging (FCM) |
| Service Worker | Firebase Service Worker |
| Theme | Dark Mode UI |

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  Frontend Layer (Templates)                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ UI Routes: / | /report | /missing-list | /dashboard |      │ │
│ │            /face-search | /login | /signup                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────────┐
│                    Flask Application                             │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Route Blueprints (Business Logic)                           ││
│ │ • ui.py → HTML page routes                                  ││
│ │ • missing_persons.py → Missing person CRUD                  ││
│ │ • crime_data.py → Crime incident management                 ││
│ │ • ai_features.py → Face matching & ML predictions           ││
│ │ • dashboard.py → Analytics & statistics                     ││
│ │ • auth.py → Authentication & authorization                  ││
│ │ • notifications.py → Firebase device management             ││
│ └──────────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Utility Layer (Business Logic & Integrations)               ││
│ │ • face_utils.py → AI face matching engine                   ││
│ │ • ml_utils.py → Crime risk prediction (Random Forest)       ││
│ │ • firebase_utils.py → Push notification delivery            ││
│ │ • helpers.py → File validation utilities                    ││
│ │ • seed_data.py → Demo data initialization                   ││
│ └──────────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Data Layer (SQLAlchemy ORM Models)                          ││
│ │ • MissingPerson, CrimeData, User, Device, AlertHistory     ││
│ └──────────────────────────────────────────────────────────────┘│
└────────┬──────────────────────┬──────────────────────┬───────────┘
         │                      │                      │
    ┌────▼────────┐     ┌──────▼──────┐     ┌────────▼────────┐
    │   Database   │     │ AI/ML Layer │     │  Firebase (FCM) │
    │ MySQL/SQLite │     │ DeepFace    │     │ Notifications   │
    │              │     │ face_recog  │     │ Service         │
    │ - missing_   │     │ scikit-learn│     │                 │
    │   persons    │     │ OpenCV      │     │ Device Tokens   │
    │ - crimes     │     │             │     │ Push Messages   │
    │ - users      │     │ Face        │     └─────────────────┘
    │ - devices    │     │ Embeddings  │
    │ - alerts     │     └─────────────┘
    └─────────────┘
```

### Data Flow Architecture

```
1. User Reports Missing Person
   └─► Upload Photo → File Validation
       └─► Store in /uploads
           └─► Generate Face Encoding (DeepFace/face_recognition)
               └─► Store Encoding in Database
                   └─► DB Updated ✓

2. User Runs Face Search
   └─► Upload Query Photo
       └─► Extract Face Encoding
           └─► Compare against all stored encodings (cosine similarity)
               └─► Return matches ranked by confidence %
                   └─► Trigger Firebase notification if high confidence match

3. Crime Analytics
   └─► Police add crime incident
       └─► Geocode location (lat/lng)
           └─► ML model analyzes historical patterns
               └─► Generate risk predictions (High/Medium/Low)
                   └─► Display on hotspot heatmap
                       └─► Send alerts to registered devices in high-risk areas

4. User Registration & Login
   └─► User submits credentials
       └─► Password hashed with Werkzeug
           └─► User role assigned (Public/Police/Admin)
               └─► Firebase config injected
                   └─► Access to dashboards based on role
```

---

## Feature Description

### 🔍 1. Missing Person Management
**Objective**: Enable public and police to report and track missing persons.

**Features**:
- **Report Missing Person**: Upload photo, name, age, last seen location, description, contact info
- **Photo Storage**: Secure file upload with validation (jpg, jpeg, png max 16MB)
- **Face Encoding**: Automatic generation of face embeddings for facial recognition
- **Status Tracking**: Mark persons as "missing" or "found"
- **Search & Filter**: Query by status, name, date reported
- **REST API**: CRUD endpoints for integration

**API Endpoints**:
```
POST   /api/missing/add                  - Add new missing person
GET    /api/missing/list                 - List all missing persons
GET    /api/missing/<id>                 - Get specific person details
PUT    /api/missing/<id>/status          - Update person status
DELETE /api/missing/<id>                 - Delete person record
```

---

### 🤖 2. AI-Powered Face Matching
**Objective**: Quickly identify potential matches using facial recognition.

**Technology**: 
- **Primary**: DeepFace library (Facenet512 model) for high-accuracy embeddings
- **Fallback**: face_recognition library (if DeepFace unavailable)
- **Similarity**: Cosine similarity on 128-512d vectors (0-100% scale)
- **Threshold**: Configurable (default 70% confidence)

**Features**:
- **Upload Query Image**: Provide a photo to search against
- **Automatic Matching**: Compare face embeddings with all stored persons
- **Ranked Results**: Display matches sorted by confidence %
- **One-to-Many Search**: Find multiple potential matches
- **Graceful Fallback**: Works with or without AI libraries (mock mode)

**API Endpoints**:
```
POST   /api/ai/match-face                - Run facial recognition search
POST   /api/ai/rebuild-face-encodings    - Regenerate all face embeddings
GET    /api/ai/predict-risk              - Get ML-predicted risk areas
```

**Example Response**:
```json
{
  "matches": [
    {
      "person_id": 5,
      "name": "John Doe",
      "confidence": 89.3,
      "age": 28,
      "last_seen": "MG Road, Bangalore"
    },
    {
      "person_id": 12,
      "name": "Jane Smith",
      "confidence": 74.5,
      "age": 31,
      "last_seen": "Koramangala, Bangalore"
    }
  ]
}
```

---

### 📊 3. Crime Data Analytics
**Objective**: Track and visualize crime incidents to identify patterns.

**Features**:
- **Add Crime Incident**: Location, type, severity (1-5), date, GPS coordinates
- **Aggregate Statistics**: Crimes by location, crime type, severity distribution
- **12-Month Trends**: Historical comparison of missing persons vs crimes
- **Geographic Mapping**: Visualize crimes by location (lat/lng support)
- **Demo Reseeding**: Populate sample data for testing

**API Endpoints**:
```
POST   /api/crime/add                    - Add new crime incident
GET    /api/crime/list                   - List all crimes
GET    /api/crime/stats                  - Aggregate statistics
GET    /api/crime/trends                 - 12-month trend analysis
POST   /api/crime/reseed                 - Reseed demo data
```

**Sample Crime Data**:
```python
Locations: MG Road, Koramangala, Whitefield, Jayanagar, Indiranagar
Crime Types: Theft, Robbery, Assault, Cybercrime, Pickpocketing, Fraud
Severity: 1 (Low) to 5 (Critical)
```

---

### 🎯 4. ML-Driven Risk Prediction
**Objective**: Identify high-risk areas to allocate resources effectively.

**Technology**:
- **Algorithm**: scikit-learn Random Forest Classifier
- **Features**: Total incidents, avg severity, unique crime types, recent activity
- **Output**: Risk level (High/Medium/Low) per location

**Risk Classification**:
- **High**: Top 25% of locations by predicted risk
- **Medium**: Middle 50%
- **Low**: Bottom 25%

**Features**:
- **Predictive Analytics**: Identify emerging crime hotspots
- **Hotspot Analysis**: Geographic clustering of high-risk zones
- **Resource Allocation**: Guide police deployment
- **Trend Analysis**: Monthly crime patterns

**API Endpoints**:
```
GET    /api/ai/predict-risk              - Get risk predictions for all locations
GET    /api/dashboard/crime-density      - Heat map density data
```

---

### 🔔 5. Push Notifications (Firebase)
**Objective**: Keep stakeholders informed in real-time.

**Technology**: Firebase Cloud Messaging (FCM)

**Features**:
- **Device Registration**: Register browser/mobile device tokens
- **Batch Delivery**: Send to 1000+ devices per request
- **Alert Types**:
  - Face match found (confidence > threshold)
  - High-risk location alerts
  - Missing person status updates
- **Deduplication**: Prevent duplicate alerts within 6-hour window
- **Multi-Platform**: iOS, Android, Web browsers
- **Service Worker**: Background notification handling

**API Endpoints**:
```
POST   /api/notifications/register       - Register device token
POST   /api/notifications/unregister     - Unregister device token
```

---

### 👥 6. Role-Based Access Control (RBAC)
**Objective**: Ensure secure, multi-stakeholder access with appropriate permissions.

**Roles**:

| Role | Permissions |
|------|-----------|
| **Public** | • View missing persons list<br/>• Report missing persons<br/>• Register for push notifications |
| **Police** | All Public permissions +<br/>• Access police dashboard<br/>• Run face search<br/>• Add crime incidents<br/>• View crime analytics<br/>• Mark persons as found |
| **Admin** | All Police permissions +<br/>• User management<br/>• System configuration<br/>• Data access logs |

**Authentication**:
- Secure login with password hashing (Werkzeug)
- Session management via Flask-Login
- Role assignment on signup
- Redirect to login for unauthorized access

**API Endpoints**:
```
POST   /login                            - Public/Admin login
POST   /police-login                     - Police login
POST   /signup                           - User registration
POST   /logout                           - User logout
```

---

### 📱 7. Responsive Web Dashboard
**Objective**: Provide intuitive, data-rich interface for decision-makers.

**Dashboard Features** (Police/Admin):
- **Summary Cards**:
  - Total missing persons (by status)
  - Total crimes
  - Persons marked found
  - High-risk locations count

- **Crime Analytics Charts**:
  - Crimes by location (pie chart)
  - Crimes by type (bar chart)
  - Monthly trends (line chart)

- **Risk Heatmap**: Geographic visualization of crime hotspots

- **Recent Activity**:
  - Latest missing persons reports
  - Recent crime incidents
  - Top alert notifications

**UI Features**:
- Dark theme (reduces eye strain)
- Responsive design (mobile/tablet/desktop)
- Real-time data refresh
- Interactive charts (drill-down capability)
- Export functionality

---

## Database Schema

### 1. missing_persons Table
```sql
CREATE TABLE missing_persons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    age INT,
    photo VARCHAR(255),              -- Filename/path to uploaded photo
    last_seen VARCHAR(255),          -- Location description
    description TEXT,                -- Additional details
    contact VARCHAR(120),            -- Reporter contact info
    status ENUM('missing', 'found') DEFAULT 'missing',
    date_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_date (date_reported)
);
```

### 2. crime_data Table
```sql
CREATE TABLE crime_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(255) NOT NULL,
    type VARCHAR(120),               -- Crime category
    severity TINYINT DEFAULT 1,      -- Scale: 1-5
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    lat DOUBLE,                      -- Latitude for mapping
    lng DOUBLE,                      -- Longitude for mapping
    INDEX idx_location (location),
    INDEX idx_type (type),
    INDEX idx_date (date)
);
```

### 3. users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Public',  -- 'Public', 'Police', 'Admin'
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email)
);
```

### 4. notification_devices Table
```sql
CREATE TABLE notification_devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) UNIQUE NOT NULL,     -- Firebase FCM token
    platform VARCHAR(50),                    -- 'iOS', 'Android', 'Web'
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_token (token)
);
```

### 5. alert_history Table
```sql
CREATE TABLE alert_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(100),         -- 'face_match', 'risk_alert', etc.
    reference VARCHAR(255),          -- ID of related entity
    message TEXT,                    -- Alert message
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created (created_on)
);
```

**Database Configuration**:
- **Engine**: InnoDB (transactions, foreign keys)
- **Charset**: utf8mb4 (Unicode support)
- **Collation**: utf8mb4_unicode_ci

---

## Module Documentation

### Core Application Files

#### `app.py` - Flask Application Factory
**Purpose**: Main entry point for the application.

**Key Functions**:
- `create_app()`: Initializes Flask app, database, blueprints
- Registers all route blueprints with URL prefixes
- Creates database tables on startup
- Seeds demo data

**Blueprints Registered**:
```python
/api/missing       → missing_persons.py
/api/crime         → crime_data.py
/api/ai            → ai_features.py
/api/dashboard     → dashboard.py
/api/notifications → notifications.py
/                  → ui.py, auth.py
```

---

#### `config.py` - Configuration Management
**Purpose**: Centralized configuration for database, uploads, thresholds.

**Key Configuration Variables**:
```python
# Database
SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/missing_tracker'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# File Uploads
UPLOAD_FOLDER = '/path/to/missing_tracker/static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Face Recognition Threshold
FACE_MATCH_CONFIDENCE_THRESHOLD = 70.0  # 70% confidence

# Firebase
FIREBASE_PROJECT_ID = 'your-firebase-project'
FIREBASE_PRIVATE_KEY_ID = '...'
FIREBASE_PRIVATE_KEY = '...'
```

---

### Route Modules

#### `routes/ui.py` - HTML Page Routes
**Purpose**: Serve HTML templates for user-facing pages.

**Key Routes**:
```python
@app.route('/')                          # Home page
@app.route('/report')                    # Report missing person form
@app.route('/missing-list')              # List of all missing persons
@app.route('/dashboard')                 # Police/Admin dashboard
@app.route('/face-search')               # Face search tool
@app.route('/notifications/settings')    # Notification settings
```

**Role-Based Access**:
- Dashboard/face-search accessible only to Police/Admin
- Public users redirected to login if unauthorized

---

#### `routes/missing_persons.py` - Missing Person Management
**Purpose**: CRUD operations for missing person reports.

**Key Endpoints**:
```python
POST   /api/missing/add
    - Parameters: name, age, photo (file), last_seen, description, contact
    - Returns: person_id, success message
    - Triggers: Face encoding generation

GET    /api/missing/list
    - Query params: status (optional), limit, offset
    - Returns: Array of person objects

GET    /api/missing/<id>
    - Returns: Detailed person record

PUT    /api/missing/<id>/status
    - Parameters: status (missing/found)
    - Returns: Updated person

DELETE /api/missing/<id>
    - Returns: Success/error message
```

---

#### `routes/crime_data.py` - Crime Incident Management
**Purpose**: Track and analyze crime incidents.

**Key Endpoints**:
```python
POST   /api/crime/add
    - Parameters: location, type, severity (1-5), lat, lng
    - Returns: crime_id, success message

GET    /api/crime/list
    - Query params: location (optional), limit, offset
    - Returns: Array of crime records

GET    /api/crime/stats
    - Returns: JSON with stats by location, crime type, severity distribution
    - Example: { "by_location": {...}, "by_type": {...} }

GET    /api/crime/trends
    - Returns: 12-month monthly statistics for missing persons and crimes
    - For time series visualization

POST   /api/crime/reseed
    - Repopulates demo data (for testing)
    - Returns: success message
```

---

#### `routes/ai_features.py` - Face Matching & Risk Prediction
**Purpose**: AI-powered features for facial recognition and ML predictions.

**Key Endpoints**:
```python
POST   /api/ai/match-face
    - Parameters: query_image (file)
    - Returns: matches array with confidence percentages
    - Triggers: Firebase notification if high-confidence match

POST   /api/ai/rebuild-face-encodings
    - Regenerates all face embeddings from stored photos
    - Returns: success message, count of processed photos

GET    /api/ai/predict-risk
    - Returns: JSON with risk predictions per location
    - Example: { "locations": [{"name": "MG Road", "risk": "High", ...}] }
```

---

#### `routes/dashboard.py` - Analytics & Statistics
**Purpose**: Aggregate data for dashboard visualization.

**Key Endpoints**:
```python
GET    /api/dashboard/summary
    - Returns: Summary statistics
    - Fields: total_missing, total_found, total_crimes, 
              recent_reports, crimes_by_location, crimes_by_type

GET    /api/dashboard/crime-density
    - Returns: Heatmap data with lat/lng and crime density
    - For geographic visualization
```

**Response Example**:
```json
{
  "total_missing": 45,
  "total_found": 12,
  "total_crimes": 156,
  "recent_reports": [...],
  "trends_12_months": [
    {"month": "June 2025", "missing": 3, "found": 2, "crimes": 12},
    ...
  ]
}
```

---

### Utility Modules

#### `utils/face_utils.py` - Face Recognition Engine
**Purpose**: Facial recognition and face encoding management.

**Key Functions**:

```python
def update_face_encodings(missing_person_id, photo_path):
    """Generate and store face encoding for a person"""
    # 1. Load photo
    # 2. Extract face encoding (DeepFace or face_recognition)
    # 3. Store encoding in pickle file or database
    # 4. Return success/error

def find_matching_person(query_photo_path, confidence_threshold=70.0):
    """Search for matching missing persons"""
    # 1. Extract face encoding from query photo
    # 2. Load all stored encodings
    # 3. Compute cosine similarity for each
    # 4. Filter by confidence threshold
    # 5. Return sorted matches

def rebuild_all_encodings():
    """Regenerate encodings for all stored photos"""
    # 1. Iterate through all missing persons
    # 2. Regenerate face encodings
    # 3. Update storage
    # 4. Return count of processed photos
```

**Supported Models**:
- **Primary**: DeepFace (Facenet512) - 512-dimensional embeddings
- **Fallback**: face_recognition - 128-dimensional embeddings
- **Fallback**: Mock (for testing without AI)

---

#### `utils/ml_utils.py` - Crime Analytics & Risk Prediction
**Purpose**: Machine learning-driven crime analysis.

**Key Functions**:

```python
def predict_risk_areas():
    """Use Random Forest to predict high-risk areas"""
    # 1. Aggregate per-location crime statistics
    # 2. Engineer features:
    #    - total incidents, avg severity
    #    - unique crime types
    #    - incidents in last 30/90 days
    # 3. Train Random Forest classifier
    # 4. Predict risk levels: High/Medium/Low
    # 5. Return predictions per location

def get_hotspot_analysis():
    """Identify crime hotspots"""
    # 1. Aggregate crimes by location
    # 2. Compute concentration metrics
    # 3. Rank by severity/frequency
    # 4. Return top 10 hotspots

def aggregate_location_stats(location):
    """Get statistics for a specific location"""
    # Return: total crimes, avg severity, crime types, recent activity
```

**ML Algorithm**: Random Forest Classifier
- **Training**: Historical crime data
- **Features**: Crime count, severity, types, temporal patterns
- **Output**: Risk classification (High 25%, Medium 50%, Low 25%)

---

#### `utils/firebase_utils.py` - Push Notifications
**Purpose**: Firebase Cloud Messaging integration.

**Key Functions**:

```python
def notify_face_match(person_id, confidence, match_ids):
    """Send notification when face match found"""
    # 1. Get registered device tokens
    # 2. Check deduplication (prevent duplicate within 6 hours)
    # 3. Compose notification message
    # 4. Send via Firebase FCM (batches of 1000)
    # 5. Log to alert_history

def notify_high_risk_locations(high_risk_zones):
    """Alert users about high-risk areas"""
    # 1. Get user device tokens
    # 2. Compose location-based alerts
    # 3. Send batch notifications
    # 4. Log alerts

def _send_notification(tokens, title, body):
    """Internal function to send batch notifications"""
    # 1. Chunk tokens into 1000-token batches (FCM limit)
    # 2. Send each batch to Firebase
    # 3. Handle errors gracefully
```

**Deduplication**:
- Prevents duplicate alerts within 6-hour window
- Stores alert history for tracking
- Respects user preferences

---

#### `utils/helpers.py` - Utility Functions
**Purpose**: General-purpose helper functions.

**Key Functions**:

```python
def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    # Allowed: jpg, jpeg, png
    # Max size: 16 MB (checked at upload)
    # Returns: True/False
```

---

#### `utils/seed_data.py` - Demo Data Initialization
**Purpose**: Populate sample data on application startup.

**Functions**:

```python
def seed_crime_data():
    """Populate sample crime incidents"""
    # Sample locations: MG Road, Koramangala, Whitefield, Jayanagar, Indiranagar
    # Crime types: Theft, Robbery, Assault, Cybercrime, Pickpocketing, Fraud
    # Severity: Random 1-5
    # Only seeds if table is empty

def seed_missing_persons():
    """Populate sample missing person reports"""
    # Only seeds if table is empty
    # Realistic names, ages, descriptions
```

---

## API Documentation

### Authentication Endpoints

```
POST /login
    - Body: { "username": "...", "password": "..." }
    - Returns: { "success": true, "user_id": 1, "role": "Police" }

POST /police-login
    - Same as above but validates police role

POST /signup
    - Body: { "username": "...", "email": "...", "password": "...", "role": "Public" }
    - Returns: { "success": true, "user_id": 2 }

POST /logout
    - Returns: { "success": true }
```

### Missing Persons API

```
POST /api/missing/add
    - Content-Type: multipart/form-data
    - Body:
        - name: string (required)
        - age: integer (optional)
        - photo: file (required, jpg/jpeg/png, max 16MB)
        - last_seen: string (required)
        - description: string (optional)
        - contact: string (required)
    - Returns: { "success": true, "person_id": 5, "message": "..." }

GET /api/missing/list?status=missing&limit=10&offset=0
    - Returns: { "persons": [...], "total": 45 }

GET /api/missing/5
    - Returns: { "person": { "id": 5, "name": "...", "age": 28, ... } }

PUT /api/missing/5/status
    - Body: { "status": "found" }
    - Returns: { "success": true, "person": { ... } }

DELETE /api/missing/5
    - Returns: { "success": true, "message": "..." }
```

### Crime Data API

```
POST /api/crime/add
    - Body: { "location": "...", "type": "...", "severity": 3, "lat": 13.0, "lng": 77.5 }
    - Returns: { "success": true, "crime_id": 42 }

GET /api/crime/list?location=&limit=20
    - Returns: { "crimes": [...], "total": 156 }

GET /api/crime/stats
    - Returns: { "by_location": {...}, "by_type": {...}, "severity_dist": {...} }

GET /api/crime/trends
    - Returns: { "monthly": [{"month": "June", "missing": 3, "crimes": 12}, ...] }

POST /api/crime/reseed
    - Returns: { "success": true, "message": "Reseeded 50 sample crimes" }
```

### AI Features API

```
POST /api/ai/match-face
    - Content-Type: multipart/form-data
    - Body:
        - query_image: file (required)
    - Returns: { "matches": [{"person_id": 5, "confidence": 89.3, ...}, ...] }

POST /api/ai/rebuild-face-encodings
    - Returns: { "success": true, "processed": 42, "message": "..." }

GET /api/ai/predict-risk
    - Returns: { "predictions": [{"location": "...", "risk": "High"}, ...] }
```

### Dashboard API

```
GET /api/dashboard/summary
    - Returns: { "total_missing": 45, "total_found": 12, ..., "recent_reports": [...] }

GET /api/dashboard/crime-density
    - Returns: { "heatmap_data": [{"lat": 13.0, "lng": 77.5, "density": 0.8}, ...] }
```

### Notifications API

```
POST /api/notifications/register
    - Body: { "token": "firebase_token", "platform": "Web" }
    - Returns: { "success": true }

POST /api/notifications/unregister
    - Body: { "token": "firebase_token" }
    - Returns: { "success": true }
```

---

## Installation & Setup

### Quick Demo (No MySQL needed)

```powershell
# From project root
.\run_demo.ps1

# Or with custom Python
.\run_demo.ps1 -PythonExe "C:\Path\To\Python311\python.exe"
```

This creates `.venv-demo`, installs dependencies, and starts the app at `http://localhost:5000` with SQLite database.

### Full Setup with MySQL

**1. Prerequisites**
```bash
# Install Python 3.9-3.11
# Install MySQL Server 8.0+
# Install pip (latest)
```

**2. Clone Repository**
```bash
git clone <repo-url>
cd missing_tracker
```

**3. Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure Environment**
```bash
# Copy example
cp .env.example .env

# Edit .env with your settings:
# FLASK_ENV=production
# SQLALCHEMY_DATABASE_URI=mysql://user:password@localhost/missing_tracker
# FIREBASE_PROJECT_ID=your-project-id
# FIREBASE_PRIVATE_KEY=...
```

**6. Initialize Database**
```bash
# Create database in MySQL
mysql -u root -p
  > CREATE DATABASE missing_tracker;
  > EXIT;

# Run Flask app (auto-creates tables)
python app.py
```

**7. Access Application**
```
http://localhost:5000
```

---

## Usage Guide

### For Public Users

1. **Report Missing Person**
   - Click "Report" button
   - Fill form with person details and upload photo
   - Submit report

2. **Search Missing Persons**
   - Click "Missing List"
   - Browse or search for specific cases
   - Share on social media to raise awareness

3. **Enable Notifications**
   - Click "Notifications Settings"
   - Authorize browser to receive push notifications
   - Get alerts about matching persons or high-risk areas

### For Police Officers

1. **Access Dashboard**
   - Login as "Police"
   - View summary statistics and charts
   - See recent reports and top hotspots

2. **Run Face Search**
   - Go to "Face Search" tool
   - Upload photo to search against missing persons database
   - View ranked matches with confidence scores
   - Take action on positive identifications

3. **Add Crime Incident**
   - Click "Add Crime"
   - Enter location, type, severity, GPS coordinates
   - System automatically predicts risk level

4. **Analyze Crime Patterns**
   - View crime heatmap by location
   - Check 12-month trends
   - Identify emerging hotspots
   - Use ML-predicted risk areas for resource allocation

### For Administrators

- All Police capabilities
- User management
- System configuration
- Access logs and audit trail

---

## Future Enhancements

### Phase 2 Features
1. **Mobile Application** (iOS/Android)
   - Native app with offline face matching
   - QR code generation for missing person posters
   - Direct camera integration

2. **Advanced ML Models**
   - Deep learning for age/gender estimation
   - Behavior pattern recognition
   - Multimodal search (face + description)

3. **CCTV Integration**
   - Real-time face detection in surveillance feeds
   - Automatic alerts on match detection
   - Video clip extraction

4. **Blockchain Integration**
   - Immutable alert history
   - Distributed alert network
   - Transparent case tracking

5. **Cross-Border Collaboration**
   - Multi-jurisdiction database sharing
   - International face matching
   - Coordinated alerts

### Technical Improvements
- [ ] Microservices architecture (scalability)
- [ ] Kubernetes deployment (containerization)
- [ ] GraphQL API (flexible querying)
- [ ] Real-time WebSocket updates
- [ ] Advanced caching (Redis)
- [ ] Elasticsearch integration (fast search)

---

## Conclusion

**TraceNet** is a comprehensive, production-ready system that combines modern AI, ML, and web technologies to address a critical societal need: finding missing persons and preventing crime. By leveraging facial recognition, predictive analytics, and real-time notifications, the platform empowers law enforcement and the public to work together more effectively.

The modular architecture allows for easy scaling, integration with external systems, and addition of new features. With proper configuration and deployment, TraceNet can make a real difference in communities worldwide.

---

## Project Metadata
- **Version**: 1.0.0
- **Release Date**: June 2026
- **License**: MIT (or your chosen license)
- **Repository**: [GitHub URL]
- **Documentation**: [Wiki/Docs URL]
- **Support**: [Support Email/Channel]

---

**Document Created**: June 2, 2026
**Last Updated**: June 2, 2026
**Prepared For**: Project Submission & Documentation

