# 🔧 Known Issues & Troubleshooting Guide

## Overview
Comprehensive list of known issues, error conditions, and solutions for TraceNet.

---

## Table of Contents
1. [Database Issues](#database-issues)
2. [Face Recognition Issues](#face-recognition-issues)
3. [File Upload Issues](#file-upload-issues)
4. [Authentication Issues](#authentication-issues)
5. [API Issues](#api-issues)
6. [UI/Frontend Issues](#uifrontend-issues)
7. [Performance Issues](#performance-issues)
8. [Firebase/Notifications Issues](#firebasenotifications-issues)

---

## Database Issues

### Issue 1: MySQL Connection Refused

**Error Message:**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost' (111)")
```

**Cause:** MySQL service not running or credentials incorrect

**Solution:**
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL if stopped
sudo systemctl start mysql

# Verify connection
mysql -h localhost -u root -p
```

**Workaround:** Use SQLite for demo:
```bash
.\run_demo.ps1  # Windows
python run_demo.py  # Linux/Mac
```

---

### Issue 2: Database Migration Error

**Error Message:**
```
sqlalchemy.exc.SQLAlchemyError: Cannot render database-agnostic type <class 'sqlalchemy.sql.sqltypes.JSON'>
```

**Cause:** Incompatible SQLAlchemy version with database

**Solution:**
```bash
# Update SQLAlchemy
pip install --upgrade SQLAlchemy

# Or downgrade to compatible version
pip install SQLAlchemy==2.0.50
```

---

### Issue 3: Table Already Exists

**Error Message:**
```
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1050, "Table 'users' already exists")
```

**Cause:** Database tables already created from previous run

**Solution:**
```python
# In Python shell
from app import create_app
from models.database import db

app = create_app()
with app.app_context():
    db.drop_all()  # WARNING: Deletes all data
    db.create_all()  # Recreates tables
```

---

### Issue 4: Foreign Key Constraint Fails

**Error Message:**
```
IntegrityError: (pymysql.err.IntegrityError) (1452, 'Cannot add or update a child row: a foreign key constraint fails')
```

**Cause:** Attempting to reference non-existent parent record

**Solution:**
```python
# Verify parent record exists before creating child
person = MissingPerson.query.get(person_id)
if person:
    # Safe to create related record
    pass
else:
    # Handle error
    raise ValueError(f"Person {person_id} not found")
```

---

### Issue 5: Database Locked (SQLite)

**Error Message:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Another process has database file locked

**Solution:**
```bash
# Find process locking database
lsof | grep missing_tracker.db

# Kill process (if necessary)
kill -9 <PID>

# Or delete database and recreate
rm instance/missing_tracker.db
```

---

## Face Recognition Issues

### Issue 6: DeepFace Model Download Fails

**Error Message:**
```
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]>
```

**Cause:** SSL certificate verification failure when downloading model

**Solution:**
```bash
# Option 1: Disable SSL verification (not recommended for production)
pip install --upgrade certifi

# Option 2: Download model manually
python -c "from deepface import DeepFace; DeepFace.build_model('Facenet512')"

# Option 3: Use environment variable
set REQUESTS_CA_BUNDLE=

# Option 4: Use alternative model
# Modify config to use different model
```

---

### Issue 7: Face Encoding Generation Fails

**Error Message:**
```
ValueError: Face not detected
```

**Cause:** Image doesn't contain detectable face

**Solution:**
```python
# Add error handling in face_utils.py
try:
    from deepface import DeepFace
    embedding = DeepFace.represent(img_path, enforce_detection=False)
except:
    # Fallback to face_recognition
    import face_recognition
    image = face_recognition.load_image_file(img_path)
    encodings = face_recognition.face_encodings(image)
```

---

### Issue 8: Low Face Matching Accuracy

**Error Message:** Correct matches not found or confidence too low

**Cause:** 
- Threshold too high (default 70%)
- Poor image quality
- Different lighting conditions

**Solution:**
```python
# Lower confidence threshold temporarily
confidence_threshold = 60.0  # Reduced from 70%

# Or improve image quality:
# - Use clear, frontal photos
# - Ensure good lighting
# - Remove sunglasses/hats

# Update config
# In config.py
FACE_MATCH_CONFIDENCE_THRESHOLD = 60.0
```

---

### Issue 9: Encoding File Corrupted

**Error Message:**
```
EOFError: pickle data was truncated
```

**Cause:** Encodings.pkl file corrupted

**Solution:**
```bash
# Delete corrupted file
rm static/encodings.pkl

# Rebuild encodings
curl -X POST http://localhost:5000/api/ai/rebuild-face-encodings

# Or via Python
python -c "
from app import create_app
from utils.face_utils import rebuild_all_encodings
app = create_app()
with app.app_context():
    result = rebuild_all_encodings()
    print(result)
"
```

---

## File Upload Issues

### Issue 10: File Size Exceeds Limit

**Error Message:**
```
RequestEntityTooLarge: 413 Request Entity Too Large
```

**Cause:** File size > 16MB limit

**Solution:**
```python
# In config.py, increase limit
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB

# Or compress image before upload
from PIL import Image
img = Image.open('large_photo.jpg')
img.thumbnail((1024, 1024))
img.save('compressed_photo.jpg', quality=85)
```

---

### Issue 11: File Type Not Allowed

**Error Message:**
```
Invalid file type. Allowed: jpg, jpeg, png
```

**Cause:** Uploading unsupported file format

**Solution:**
```bash
# Convert file to supported format
# Using ImageMagick
convert input_file.bmp output_file.jpg

# Using Python PIL
from PIL import Image
img = Image.open('file.bmp')
img.save('file.jpg')
```

---

### Issue 12: Upload Directory Permission Denied

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: './static/uploads/filename.jpg'
```

**Cause:** Upload directory not writable

**Solution:**
```bash
# Linux/Mac
chmod 755 static/uploads/
chmod 777 static/uploads/  # More permissive

# Windows (PowerShell)
icacls "static\uploads" /grant:r "$env:USERNAME:(F)"
```

---

## Authentication Issues

### Issue 13: Session Expires Quickly

**Error Message:** User logged out unexpectedly

**Cause:** Session timeout too short

**Solution:**
```python
# In config.py, increase session lifetime
PERMANENT_SESSION_LIFETIME = 24 * 60 * 60  # 24 hours

# Also set in app
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=24)
```

---

### Issue 14: Password Hashing Error

**Error Message:**
```
ValueError: Not a valid bcrypt password, it must start with $2a$, $2b$, or $2y$
```

**Cause:** Werkzeug hashing algorithm mismatch

**Solution:**
```python
# Use werkzeug's built-in hashing
from werkzeug.security import generate_password_hash, check_password_hash

# In User model
def set_password(self, password):
    self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

---

### Issue 15: CORS Error on Frontend Requests

**Error Message:**
```
Access to XMLHttpRequest at 'http://localhost:5000/api/missing/list' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Cause:** CORS not properly configured

**Solution:**
```python
# In app.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

# Or configure in config
CORS_ORIGINS = ['http://localhost:3000', 'https://yourdomain.com']
```

---

## API Issues

### Issue 16: Missing Required Query Parameter

**Error Message:**
```json
{
  "success": false,
  "message": "Missing required parameter: limit"
}
```

**Cause:** Required query parameter not provided

**Solution:**
```bash
# Always include required parameters
GET /api/missing/list?limit=10&offset=0

# Check API documentation for required parameters
```

---

### Issue 17: Invalid JSON in Request Body

**Error Message:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Cause:** Request body not valid JSON

**Solution:**
```bash
# Ensure Content-Type header is set
-H "Content-Type: application/json"

# Validate JSON before sending
# Use online JSON validator

# Example valid request
curl -X POST http://localhost:5000/api/crime/add \
  -H "Content-Type: application/json" \
  -d '{"location":"MG Road","type":"Theft","severity":3}'
```

---

### Issue 18: 401 Unauthorized Response

**Error Message:**
```json
{
  "success": false,
  "message": "Unauthorized access"
}
```

**Cause:** User not authenticated or session expired

**Solution:**
```bash
# 1. Login first to get session cookie
POST /auth/login

# 2. Use returned session in subsequent requests
curl -b cookies.txt -c cookies.txt http://localhost:5000/api/missing/list

# 3. Check session expiration
```

---

### Issue 19: 403 Forbidden Response

**Error Message:**
```json
{
  "success": false,
  "message": "Insufficient permissions"
}
```

**Cause:** User doesn't have required role

**Solution:**
```python
# Verify user role
# Police endpoints require "Police" or "Admin" role
# Admin endpoints require "Admin" role

# Check current user role
GET /api/user/profile

# Request role upgrade from admin
```

---

## UI/Frontend Issues

### Issue 20: Page Blank After Login

**Cause:** 
- JavaScript not loading
- Template rendering error
- CSS conflicts

**Solution:**
```bash
# Check browser console for errors
# Press F12 to open Developer Tools

# Clear cache
Ctrl+Shift+Delete (Chrome)
Cmd+Shift+Delete (Firefox)

# Hard refresh
Ctrl+F5
Cmd+Shift+R

# Check Flask template rendering
python -c "
from app import create_app
app = create_app()
with app.test_client() as client:
    resp = client.get('/')
    print(resp.status_code)
    print(resp.data[:100])
"
```

---

### Issue 21: CSS/JS Not Loading

**Error Message:** Unstyled page or non-functional buttons

**Cause:** Static files not served

**Solution:**
```bash
# Verify static directory exists
ls -la static/

# Check Flask static configuration
# In app.py
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Or in Nginx
location /static/ {
    alias /path/to/static/;
}

# Restart Flask app
python app.py
```

---

### Issue 22: File Upload Preview Not Showing

**Cause:** Image path incorrect in template

**Solution:**
```html
<!-- Correct: -->
<img src="/static/uploads/{{ filename }}" />

<!-- Incorrect: -->
<img src="uploads/{{ filename }}" />

<!-- In Python/API response: -->
"photo": "/static/uploads/photo.jpg"  # Include full path
```

---

## Performance Issues

### Issue 23: Slow Face Matching

**Cause:** 
- Large number of encodings
- Inefficient similarity computation
- ML model not optimized

**Solution:**
```python
# Use indexed queries
import numpy as np
from scipy.spatial.distance import cdist

# Vectorized cosine similarity (faster than loop)
stored_encodings = np.array([...])
query_encoding = np.array([...])
similarities = 1 - cdist([query_encoding], stored_encodings, metric='cosine')[0]

# Or use FAISS library for fast similarity search
import faiss
index = faiss.IndexFlatL2(512)
# ... build index and search
```

---

### Issue 24: High Memory Usage

**Error Message:** Application crashes or becomes very slow

**Cause:**
- Large image files not compressed
- Memory leak in loops
- Unbounded dataset queries

**Solution:**
```python
# Limit query results
persons = MissingPerson.query.limit(100).all()  # Not all()

# Compress images on upload
from PIL import Image
img = Image.open(filepath)
img.thumbnail((800, 800))
img.save(filepath, quality=85)

# Use pagination
offset = (page - 1) * limit
persons = MissingPerson.query.limit(limit).offset(offset).all()
```

---

### Issue 25: Slow Dashboard Load

**Cause:** Complex aggregation queries

**Solution:**
```python
# Cache results
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/dashboard/summary')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_summary():
    # Expensive query here
    pass

# Clear cache when data changes
cache.clear()
```

---

## Firebase/Notifications Issues

### Issue 26: Firebase Credentials Invalid

**Error Message:**
```
google.auth.exceptions.MalformedError: Failed to load service account credentials
```

**Cause:** Invalid Firebase credentials JSON

**Solution:**
```bash
# 1. Regenerate service account key
# Firebase Console > Project Settings > Service Accounts

# 2. Download new JSON file

# 3. Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json

# 4. Or pass credentials in code
from firebase_admin import credentials
cred = credentials.Certificate('serviceAccountKey.json')
```

---

### Issue 27: Push Notifications Not Received

**Cause:**
- Device token invalid or expired
- Network connectivity issue
- FCM credentials incorrect

**Solution:**
```python
# Check device token
token = NotificationDevice.query.filter_by(is_active=True).first()
print(f"Token valid: {token is not None}")

# Re-register device
POST /api/notifications/register
{
  "token": "new_token_from_device",
  "platform": "Android"
}

# Check Firebase console for errors
# Firebase Console > Messaging > Monitoring
```

---

### Issue 28: Rate Limiting on Firebase

**Error Message:**
```
quota_exceeded: Quota exceeded for quota metric 'Send Message Operations' and limit 'Send Message Operations per minute per project'
```

**Cause:** Sending too many messages too quickly

**Solution:**
```python
# Batch notifications
def send_notifications_batched(tokens, message, batch_size=500):
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i + batch_size]
        response = messaging.send_multicast(
            MulticastMessage(tokens=batch, data=message)
        )
        time.sleep(1)  # Rate limit protection

# Or configure quotas in Firebase
# Firebase Console > Quotas
```

---

## Debugging Tips

### 1. Enable Debug Logging

```python
# In app.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    logger.debug(f"Request: {request.method} {request.path}")
```

### 2. Database Query Logging

```python
# In config.py
SQLALCHEMY_ECHO = True  # Log all SQL queries
```

### 3. Flask Debug Mode

```bash
# Enable debug mode
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac
python app.py
```

### 4. Inspect Request/Response

```python
@app.after_request
def log_response(response):
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    return response
```

---

## Common Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'deepface'` | Dependency not installed | `pip install deepface` |
| `AttributeError: 'NoneType' object has no attribute...` | None value returned | Add null checks |
| `TypeError: Object of type datetime is not JSON serializable` | DateTime not converted | Use `isoformat()` method |
| `ValueError: invalid literal for int() with base 10` | Non-integer passed as ID | Validate input type |
| `ConnectionRefusedError: [Errno 111] Connection refused` | Service not running | Check service status |

---

## Getting Help

### Resources
- **Documentation**: [docs/README.md](README.md)
- **GitHub Issues**: Report bugs or ask questions
- **Stack Overflow**: Tag: `tracenet`
- **Email**: support@tracenet.local

### Reporting Issues
Include:
1. Error message (full traceback)
2. Steps to reproduce
3. System information (OS, Python version)
4. Relevant log files

---

