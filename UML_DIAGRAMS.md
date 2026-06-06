# 📊 UML Diagrams & Class Architecture

## 1. Class Diagram - Database Models

```
┌─────────────────────────────────────────┐
│              User                       │
├─────────────────────────────────────────┤
│ - id: int (PK)                          │
│ - username: str                         │
│ - email: str                            │
│ - password_hash: str                    │
│ - role: Enum (Public/Police/Admin)      │
│ - created_on: datetime                  │
├─────────────────────────────────────────┤
│ + get_id()                              │
│ + is_authenticated()                    │
│ + is_active()                           │
│ + set_password(password)                │
│ + check_password(password) → bool       │
└────────────┬────────────────────────────┘
             │
        1    │
    ┌────────┴────────┐
    │                 │
    │ 1              1│
    │                 │
    ▼                 ▼
┌────────────────────────┐  ┌──────────────────────────┐
│   MissingPerson        │  │ NotificationDevice       │
├────────────────────────┤  ├──────────────────────────┤
│ - id: int (PK)         │  │ - id: int (PK)           │
│ - name: str            │  │ - token: str (UNIQUE)    │
│ - age: int             │  │ - platform: str          │
│ - photo: str           │  │ - user_id: int (FK)      │
│ - last_seen: str       │  │ - is_active: bool        │
│ - description: str     │  │ - created_on: datetime   │
│ - contact: str         │  │ - updated_on: datetime   │
│ - status: Enum         │  ├──────────────────────────┤
│ - date_reported: dt    │  │ + register_token()       │
│ - reporter_id: int(FK) │  │ + unregister_token()     │
├────────────────────────┤  │ + mark_as_active()       │
│ + add_report()         │  │ + send_notification()    │
│ + update_status()      │  └──────────────────────────┘
│ + get_details()        │
│ + upload_photo()       │
│ + generate_encoding()  │
└─────────────┬──────────┘
              │
              │ 1:N
              │
              ▼
    ┌──────────────────────────┐
    │   FaceEncoding           │
    ├──────────────────────────┤
    │ - id: int (PK)           │
    │ - person_id: int (FK)    │
    │ - encoding: bytes        │
    │ - model_version: str     │
    │ - confidence: float      │
    │ - created_on: datetime   │
    ├──────────────────────────┤
    │ + extract_embedding()    │
    │ + compare_similarity()   │
    │ + compute_distance()     │
    └──────────────────────────┘


┌────────────────────────┐
│     CrimeData          │
├────────────────────────┤
│ - id: int (PK)         │
│ - location: str        │
│ - type: str            │
│ - severity: int (1-5)  │
│ - date: datetime       │
│ - lat: float           │
│ - lng: float           │
│ - description: str     │
│ - created_by: int (FK) │
├────────────────────────┤
│ + add_incident()       │
│ + update_severity()    │
│ + get_location_stats() │
│ + predict_risk()       │
└─────────────┬──────────┘
              │
              │ 1:N
              │
              ▼
    ┌──────────────────────────┐
    │   AlertHistory           │
    ├──────────────────────────┤
    │ - id: int (PK)           │
    │ - alert_type: str        │
    │ - reference: str         │
    │ - message: str           │
    │ - recipient_id: int(FK)  │
    │ - device_id: int (FK)    │
    │ - sent_status: Enum      │
    │ - created_on: datetime   │
    ├──────────────────────────┤
    │ + log_alert()            │
    │ + mark_sent()            │
    │ + get_delivery_status()  │
    └──────────────────────────┘
```

---

## 2. Class Diagram - API Blueprints

```
┌──────────────────────────────────────────────────┐
│         Flask Blueprint Architecture             │
└──────────────────────────────────────────────────┘

┌─────────────────┐
│  app.py         │
│  (Factory)      │
└────────┬────────┘
         │
    ┌────┴──────┬──────┬───────┬──────────────┐
    │            │      │       │              │
    ▼            ▼      ▼       ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  ui.py   │ │missing.py│ │crime.py  │ │ai.py     │ │dashboard.py  │
├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────┤
│GET /     │ │POST add  │ │POST add  │ │POST      │ │GET /summary  │
│GET /rpt  │ │GET list  │ │GET list  │ │match-face│ │GET /density  │
│GET /ml   │ │GET /<id> │ │GET stats │ │GET risk  │ │GET /trends   │
│GET /dash │ │PUT status│ │GET trend │ │POST rbl  │ └──────────────┘
│GET /face │ │DEL /<id> │ │POST rseed│ └──────────┘
│GET /login│ └──────────┘ └──────────┘
└──────────┘

│
├─ auth.py (User authentication)
│  ├─ POST /login
│  ├─ POST /police-login
│  ├─ POST /signup
│  └─ POST /logout
│
└─ notifications.py (Firebase management)
   ├─ POST /api/notifications/register
   └─ POST /api/notifications/unregister
```

---

## 3. Sequence Diagram - Face Matching Flow

```
User          Browser       Flask App       Database    DeepFace/ML
 │              │               │               │            │
 │─ Upload ─────▶│               │               │            │
 │   Photo       │               │               │            │
 │              │─ POST ────────▶│               │            │
 │              │  /api/ai/      │               │            │
 │              │  match-face    │               │            │
 │              │               │               │            │
 │              │               │─ GET Photos ─▶│            │
 │              │               │◀──────────────│            │
 │              │               │               │            │
 │              │               │─ Extract ────────────────▶│
 │              │               │  Embedding               │
 │              │               │◀──────────────────────────│
 │              │               │                           │
 │              │               │─ Load Stored ─▶          │
 │              │               │  Encodings   │           │
 │              │               │◀─────────────│           │
 │              │               │                           │
 │              │               │─ Compute ─────────────────▶│
 │              │               │  Similarity              │
 │              │               │◀──────────────────────────│
 │              │               │                           │
 │              │               │─ Rank Results ─▶          │
 │              │               │  (Confidence %)│          │
 │              │               │◀──────────────│          │
 │              │               │               │            │
 │              │◀─ JSON ─────────               │            │
 │              │  Matches      │               │            │
 │◀─ Display ───│               │               │            │
 │  Matches     │               │               │            │
 │              │               │─ Log Alert ──▶│            │
 │              │               │   (Firebase) │            │
 │              │               │◀──────────────│            │
 │              │               │               │            │
 │              │───────────────────────────────────────────▶│
 │              │               Send Notification           │
 │              │◀───────────────────────────────────────────│
```

---

## 4. Sequence Diagram - Crime Risk Prediction

```
Police         Browser         Flask App      Database      ML Model
  │              │               │              │              │
  │─ View ──────▶│               │              │              │
  │  Dashboard   │               │              │              │
  │              │─ GET /api/ ──▶│              │              │
  │              │  dashboard/   │              │              │
  │              │  summary      │              │              │
  │              │               │              │              │
  │              │               │─ Query All ─▶│              │
  │              │               │  Crimes     │              │
  │              │               │◀─────────────│              │
  │              │               │              │              │
  │              │               │─ Aggregate ──────────────▶│
  │              │               │  Stats      │            │
  │              │               │◀──────────────────────────│
  │              │               │              │              │
  │              │               │─ Train RF ───────────────▶│
  │              │               │  Classifier │            │
  │              │               │◀──────────────────────────│
  │              │               │              │              │
  │              │               │─ Predict ────────────────▶│
  │              │               │  Risk Level │            │
  │              │               │◀──────────────────────────│
  │              │               │              │              │
  │              │◀─ JSON ────────               │              │
  │              │  Risk Data    │              │              │
  │◀─ Display ───│               │              │              │
  │  Heatmap     │               │              │              │
  │  & Risk      │               │              │              │
```

---

## 5. Sequence Diagram - User Authentication

```
User          Browser         Flask App      Database    Werkzeug
  │              │               │              │            │
  │─ Click ─────▶│               │              │            │
  │  Login       │               │              │            │
  │              │─ GET /login ─▶│              │            │
  │              │               │              │            │
  │              │◀─ HTML ────────               │            │
  │              │  Form        │              │            │
  │              │               │              │            │
  │─ Enter ─────▶│               │              │            │
  │  Credentials │               │              │            │
  │              │─ POST /login ▶│              │            │
  │              │   (creds)    │              │            │
  │              │               │              │            │
  │              │               │─ GET User ──▶│            │
  │              │               │  (username) │            │
  │              │               │◀─────────────│            │
  │              │               │              │            │
  │              │               │─ Check Pass ─────────────▶│
  │              │               │  Hash       │            │
  │              │               │◀──────────────────────────│
  │              │               │              │            │
  │              │   ┌─────────────────────────┐            │
  │              │   │ Password Matches?       │            │
  │              │   │ (if YES)                │            │
  │              │   └─────────────────────────┘            │
  │              │               │              │            │
  │              │               │─ Create ─────            │
  │              │               │  Session   │            │
  │              │               │            │            │
  │              │◀─ Redirect ────               │            │
  │              │  /dashboard   │              │            │
  │◀─ Dashboard ─│               │              │            │
  │   Page       │               │              │            │
```

---

## 6. State Diagram - Missing Person Status

```
                    ┌─────────────────┐
                    │   REPORTED      │
                    └────────┬────────┘
                             │
                             │ (Initial report)
                             │
                             ▼
                    ┌─────────────────┐
                    │    MISSING      │
                    │  (Active Case)  │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
      (Found alive) │                 │ (Deceased)
                    │                 │
                    ▼                 ▼
            ┌─────────────┐  ┌──────────────┐
            │   FOUND     │  │  DECEASED    │
            └─────────────┘  └──────────────┘

Transitions:
- REPORTED → MISSING (automatic on creation)
- MISSING → FOUND (manual update by police/admin)
- MISSING → DECEASED (manual update by police/admin)
- FOUND → MISSING (can reopen case if needed)
```

---

## 7. Component Diagram - System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Layer                              │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│ │   Browser    │ │   Mobile     │ │   Desktop    │             │
│ │   (Web UI)   │ │   (Native)   │ │   (Electron) │             │
│ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘             │
└────────┼──────────────────┼────────────────┼────────────────────┘
         │                  │                │
         └──────────────────┼────────────────┘
                            │ HTTP/REST/WebSocket
                            │
         ┌──────────────────▼────────────────┐
         │   API Gateway / Load Balancer     │
         └──────────────────┬────────────────┘
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     ▼                      ▼                      ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Web Server    │ │   Web Server    │ │   Web Server    │
│   (Flask)       │ │   (Flask)       │ │   (Flask)       │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐ │
│ │ Routes      │ │ │ Routes      │ │ │ Routes      │ │
│ │ (Blueprints)│ │ │ (Blueprints)│ │ │ (Blueprints)│ │
│ ├─────────────┤ │ ├─────────────┤ │ ├─────────────┤ │
│ │ Middleware  │ │ │ Middleware  │ │ │ Middleware  │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘ │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐ │
│ │ ORM Layer   │ │ │ ORM Layer   │ │ │ ORM Layer   │ │
│ │(SQLAlchemy) │ │ │(SQLAlchemy) │ │ │(SQLAlchemy) │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘ │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │ Connection Pooling
                             │
         ┌───────────────────▼───────────────────┐
         │   Database (MySQL)                    │
         │ ┌─────────────────────────────────┐  │
         │ │ USERS                           │  │
         │ │ MISSING_PERSONS                 │  │
         │ │ CRIME_DATA                      │  │
         │ │ NOTIFICATION_DEVICES            │  │
         │ │ ALERT_HISTORY                   │  │
         │ └─────────────────────────────────┘  │
         └───────────────────────────────────────┘


         ┌──────────────────────────────────────┐
         │   External Services Integration      │
         │ ┌───────────────────────────────┐   │
         │ │ Firebase Cloud Messaging      │   │
         │ │ (Push Notifications)          │   │
         │ ├───────────────────────────────┤   │
         │ │ DeepFace / face_recognition   │   │
         │ │ (AI Face Matching)            │   │
         │ ├───────────────────────────────┤   │
         │ │ scikit-learn                  │   │
         │ │ (ML Risk Prediction)          │   │
         │ └───────────────────────────────┘   │
         └──────────────────────────────────────┘
```

---

## 8. Activity Diagram - Missing Person Reporting

```
                         (Start)
                            │
                            ▼
                   ┌────────────────────┐
                   │ User Visits Report │
                   │     Page           │
                   └────────┬───────────┘
                            │
                            ▼
                   ┌────────────────────┐
                   │ Fill Report Form   │
                   │ - Name, Age, Photo,│
                   │ - Location, Contact│
                   └────────┬───────────┘
                            │
                            ▼
                   ┌────────────────────┐
                   │ Upload Photo File  │
                   └────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │ File Valid?    │
                    │ (jpg,jpeg,png)  │
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │  (YES)   (NO)  │
                    │                │
      ┌─────────────▼──┐      ┌──────▼────────────┐
      │ Save to Server │      │ Show Error Message│
      └─────────────┬──┘      └──────┬───────────┘
                    │               │
      ┌─────────────▼──────────────┐│
      │                            ││
      │ Generate Face Encoding    │
      │ (DeepFace / face_recog)   │
      └─────────────┬──────────────┘
                    │
                    ▼
      ┌──────────────────────────┐
      │ Store in Database        │
      │ - Person record          │
      │ - Face encoding (pickle) │
      └─────────────┬────────────┘
                    │
                    ▼
      ┌──────────────────────────┐
      │ Send Notification Alert  │
      │ to Registered Devices    │
      └─────────────┬────────────┘
                    │
                    ▼
      ┌──────────────────────────┐
      │ Display Success Message  │
      │ & Case Reference #       │
      └─────────────┬────────────┘
                    │
                    ▼
                 (End)
```

---

## 9. Deployment Diagram - Production Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Internet / Users                           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              AWS CloudFront (CDN)                            │
│  - Static assets caching                                    │
│  - SSL/TLS termination                                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│            Application Load Balancer (ALB)                   │
│  - Route traffic to multiple instances                      │
│  - Health checks                                            │
│  - SSL certificates                                         │
└────┬─────────────┬──────────────────────┬────────────────────┘
     │             │                      │
     ▼             ▼                      ▼
┌──────────┐ ┌──────────┐            ┌──────────┐
│  Flask   │ │  Flask   │   ...      │  Flask   │
│ Instance │ │ Instance │            │ Instance │
│ (Gunicorn)│ │(Gunicorn)│            │(Gunicorn)│
│    1     │ │    2     │            │    N     │
└────┬─────┘ └────┬─────┘            └────┬─────┘
     │             │                      │
     └─────────────┼──────────────────────┘
                   │
                   ▼ (Connection Pool)
        ┌──────────────────────────┐
        │    RDS MySQL Database    │
        │  - Multi-AZ deployment   │
        │  - Automated backups     │
        │  - Read replicas         │
        └──────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│                   External Services                          │
├──────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Firebase (FCM) - Push Notifications                      ││
│ └──────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────┐│
│ │ S3 / Cloud Storage - Photo uploads                       ││
│ └──────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────┐│
│ │ CloudWatch - Logging & Monitoring                        ││
│ └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

---

## 10. Data Flow Diagram (Level 1)

```
                     ┌─────────────┐
                     │   Public    │
                     │    Users    │
                     └──────┬──────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌────────────┐ ┌──────────────┐
    │ Report Miss- │ │ View Cases │ │ Receive Push │
    │ ing Persons  │ │ & Alerts   │ │Notifications │
    └──────┬───────┘ └─────┬──────┘ └──────┬───────┘
           │                │              │
           │                │              │
           └────────────────┼──────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────┐
    │   TraceNet Application                   │
    │  ┌────────────────────────────────────┐ │
    │  │ • Process reports                  │ │
    │  │ • Generate encodings               │ │
    │  │ • Run ML predictions               │ │
    │  │ • Send notifications               │ │
    │  └────────────────────────────────────┘ │
    └──────────────┬───────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────┐
        │                     │          │
        ▼                     ▼          ▼
    ┌────────┐          ┌──────────┐ ┌──────────┐
    │Database│          │ Firebase │ │AI/ML Svc.│
    │Storage │          │(FCM/msgs)│ │(DeepFace)│
    └────────┘          └──────────┘ └──────────┘


    ┌──────────────┐
    │    Police    │
    │   Officers   │
    └──────┬───────┘
           │
    ┌──────┼──────────────┐
    │      │              │
    ▼      ▼              ▼
┌──────┐ ┌─────┐ ┌───────────┐
│Dash. │ │Face │ │Add Crimes │
│Stats │ │Srch │ │& Analytics│
└──────┘ └─────┘ └───────────┘
```

