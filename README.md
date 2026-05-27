# TraceNet – Missing Person Tracking & Crime Pattern Analysis

A full-stack AI-powered web application built with **Flask**, **MySQL**, **OpenCV**, **face_recognition**, and **scikit-learn**. Provides a dark-themed dashboard for reporting missing persons, running AI face searches, and visualising ML-driven crime risk predictions.

---

## Project Structure

```
missing_tracker/
├── app.py                    # Flask application factory & entry point
├── config.py                 # App configuration (DB, uploads, thresholds)
├── requirements.txt          # Python dependencies
├── schema.sql                # MySQL schema (optional – auto-created by Flask)
├── .env.example              # Environment variable template
│
├── models/
│   └── database.py           # SQLAlchemy ORM models (MissingPerson, CrimeData)
│
├── routes/
│   ├── ui.py                 # HTML page routes (/)
│   ├── missing_persons.py    # REST: /api/missing/*
│   ├── crime_data.py         # REST: /api/crime/*
│   ├── ai_features.py        # REST: /api/ai/*  (face match, predictions)
│   └── dashboard.py          # REST: /api/dashboard/summary
│
├── utils/
│   ├── face_utils.py         # face_recognition / OpenCV face matching
│   ├── ml_utils.py           # scikit-learn crime risk prediction
│   ├── seed_data.py          # Sample crime data seeder
│   └── helpers.py            # Utility functions
│
├── templates/
│   ├── base.html             # Shared layout + navbar
│   ├── index.html            # Home page
│   ├── report.html           # Report missing person form
│   ├── missing_list.html     # Registry grid
│   ├── dashboard.html        # Crime intelligence dashboard
│   └── face_search.html      # AI face search tool
│
└── static/
    └── uploads/              # Uploaded photos (auto-created)
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 – 3.11 |
| MySQL Server | 8.0+ |
| pip | latest |
| cmake (for dlib/face_recognition) | optional |

---

## Step-by-Step Setup

### Quick Demo on Windows (SQLite)

For the fastest local run, you can use the SQLite demo path instead of setting up MySQL first.

1. Install Python 3.11.
2. From the repository root, run:

```powershell
.\run_demo.ps1
```

This helper script:
- creates a fresh `.venv-demo`
- installs `requirements-demo.txt`
- skips optional `dlib` and `face_recognition`
- starts the app with the built-in SQLite database at `http://localhost:5000`

If `py -3.11` is unavailable but you know the full path to a Python 3.11 executable, run:

```powershell
.\run_demo.ps1 -PythonExe "C:\Path\To\Python311\python.exe"
```

### 1. Clone & Enter the Project

```bash
git clone <your-repo-url>
cd missing_tracker
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Activate:
# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Face recognition (optional):**  
> Real face matching requires `dlib` and `face_recognition`. Install cmake first:
> ```bash
> # Ubuntu/Debian
> sudo apt-get install cmake libopenblas-dev liblapack-dev
>
> # macOS
> brew install cmake
>
> # Then install:
> pip install dlib face_recognition
> ```
> Without these libraries the app runs in **demo mode** and simulates face matches.

### 4. Configure MySQL

Start MySQL and create the database:

```sql
mysql -u root -p

CREATE DATABASE missing_tracker_db CHARACTER SET utf8mb4;
-- Optional: create a dedicated user
CREATE USER 'tracenet'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON missing_tracker_db.* TO 'tracenet'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/missing_tracker_db
FACE_MATCH_THRESHOLD=0.6
```

### 6. Run the Application

```bash
python app.py
```

On first start, Flask will:
- Auto-create all database tables via SQLAlchemy
- Seed 30 sample crime records for the dashboard

Open your browser at: **http://localhost:5000**

---

## API Reference

### Missing Persons

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/missing/add` | Report a new missing person (multipart/form-data) |
| `GET` | `/api/missing/list` | List all records (optional `?status=missing\|found`) |
| `GET` | `/api/missing/<id>` | Get single record |
| `PUT` | `/api/missing/<id>/status` | Update status `{status: "found"}` |
| `DELETE` | `/api/missing/<id>` | Delete record |

### Crime Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crime/add` | Add crime incident |
| `GET` | `/api/crime/list` | List all crimes |
| `GET` | `/api/crime/stats` | Aggregated stats (by location, type) |
| `GET` | `/api/crime/trends` | Monthly trend data (12 months) |

### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ai/match-face` | Upload photo → returns best match % |
| `GET` | `/api/ai/predict-risk` | ML risk predictions per location |
| `GET` | `/api/ai/hotspots` | Top 10 hotspots with enriched data |
| `POST` | `/api/ai/rebuild-encodings` | Rebuild all face encodings |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/summary` | Combined summary for dashboard |

---

## AI Features Detail

### Face Recognition

- **Library:** `face_recognition` (wraps `dlib`)  
- **Storage:** Face encodings saved as a pickle file (`utils/face_encodings.pkl`)
- **Matching:** Euclidean distance between 128-dimensional face embeddings  
- **Threshold:** Default `0.6` (configurable in `.env`)  
- **Fallback:** If `face_recognition` is not installed, demo mode returns simulated matches

### Crime Pattern Analysis (ML)

- **Algorithm:** `RandomForestClassifier` from scikit-learn
- **Features per location:** total incidents, average severity, unique crime types, last-30-day count, last-90-day count
- **Labels:** High (top 25%) / Medium / Low (bottom 25%) risk
- **Retraining:** Model is retrained automatically on every `/api/ai/predict-risk` call using latest DB data
- **Fallback:** If sklearn is unavailable, a simple count-based heuristic is used

---

## Production Deployment

```bash
# Use gunicorn instead of the built-in dev server
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

For production, also:
- Set `FLASK_ENV=production` and a strong `SECRET_KEY` in `.env`
- Use Nginx as a reverse proxy
- Store uploads on a persistent volume (e.g. S3 or NFS)

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'face_recognition'` | App runs in demo mode – this is expected. Install dlib + face_recognition for real matching. |
| `sqlalchemy.exc.OperationalError` | Check MySQL is running and `DATABASE_URL` in `.env` is correct. |
| `Access denied for user` | Verify MySQL user has GRANT ALL on `missing_tracker_db`. |
| Charts not loading | Check browser console – ensure Flask server is running on port 5000. |
| Uploads not saving | Ensure `static/uploads/` directory exists and is writable. |
