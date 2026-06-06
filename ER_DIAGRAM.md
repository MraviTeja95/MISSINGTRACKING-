# 📊 ER (Entity Relationship) Diagram & Database Documentation

## Entity Relationship Diagram (ER Diagram)

```
┌─────────────────────────┐
│      USERS              │
├─────────────────────────┤
│ PK: id                  │
│ ├─ username (UNIQUE)    │
│ ├─ email (UNIQUE)       │
│ ├─ password_hash        │
│ ├─ role (Public/Police) │
│ └─ created_on           │
└──────────────┬──────────┘
               │
               │ 1:N (One user, Many reports)
               │
               ▼
┌─────────────────────────────────────┐
│    MISSING_PERSONS                  │
├─────────────────────────────────────┤
│ PK: id                              │
│ ├─ name (VARCHAR 120)               │
│ ├─ age (INT)                        │
│ ├─ photo (VARCHAR 255, filename)    │
│ ├─ last_seen (VARCHAR 255)          │
│ ├─ description (TEXT)               │
│ ├─ contact (VARCHAR 120)            │
│ ├─ status (ENUM: missing/found)     │
│ ├─ date_reported (DATETIME)         │
│ └─ FK: reporter_id → USERS.id       │
└────────────────┬────────────────────┘
                 │
                 │ 1:N (One person, Many face encodings)
                 │
                 ▼
    ┌────────────────────────────┐
    │  FACE_ENCODINGS (optional) │
    ├────────────────────────────┤
    │ PK: id                     │
    │ ├─ FK: person_id           │
    │ ├─ encoding (BLOB/pickle)  │
    │ ├─ model_version           │
    │ └─ created_on              │
    └────────────────────────────┘


┌─────────────────────────────────────┐
│      CRIME_DATA                     │
├─────────────────────────────────────┤
│ PK: id                              │
│ ├─ location (VARCHAR 255)           │
│ ├─ type (VARCHAR 120)               │
│ ├─ severity (TINYINT 1-5)           │
│ ├─ date (DATETIME)                  │
│ ├─ lat (DOUBLE)                     │
│ ├─ lng (DOUBLE)                     │
│ ├─ description (TEXT, optional)     │
│ └─ created_by (FK → USERS.id)       │
└────────────────┬────────────────────┘
                 │
                 │ 1:N (Location, Many alerts)
                 │
                 ▼
┌──────────────────────────────────┐
│  ALERT_HISTORY                   │
├──────────────────────────────────┤
│ PK: id                           │
│ ├─ alert_type (VARCHAR 100)      │
│ ├─ reference (VARCHAR 255)       │
│ ├─ message (TEXT)                │
│ ├─ FK: device_id (optional)      │
│ └─ created_on (DATETIME)         │
└──────────────┬───────────────────┘
               │
               │ N:M via SENT_TO
               │
               ▼
┌──────────────────────────────────┐
│ NOTIFICATION_DEVICES             │
├──────────────────────────────────┤
│ PK: id                           │
│ ├─ token (VARCHAR 255, UNIQUE)   │
│ ├─ platform (iOS/Android/Web)    │
│ ├─ FK: user_id → USERS.id        │
│ ├─ created_on (DATETIME)         │
│ └─ updated_on (DATETIME)         │
└──────────────────────────────────┘
```

---

## Detailed Table Definitions

### USERS Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL COMMENT 'Unique login name',
    email VARCHAR(120) UNIQUE NOT NULL COMMENT 'Contact email',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Werkzeug hashed password',
    role ENUM('Public', 'Police', 'Admin') DEFAULT 'Public' 
        COMMENT 'Role-based access control',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    INDEX idx_role (role),
    INDEX idx_created (created_on)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Relationships**:
- 1:N with missing_persons (reporter)
- 1:N with crime_data (reporter)
- 1:N with notification_devices (subscriber)

---

### MISSING_PERSONS Table
```sql
CREATE TABLE missing_persons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL COMMENT 'Missing person full name',
    age INT COMMENT 'Age at time of report',
    photo VARCHAR(255) COMMENT 'Stored filename (stored in /static/uploads/)',
    last_seen VARCHAR(255) COMMENT 'Location description',
    description TEXT COMMENT 'Physical description, clothing, etc.',
    contact VARCHAR(120) COMMENT 'Reporter contact info',
    status ENUM('missing', 'found') DEFAULT 'missing',
    date_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
    reporter_id INT,
    
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_date_reported (date_reported),
    INDEX idx_name (name),
    FULLTEXT INDEX ft_description (description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Relationships**:
- N:1 with users (reporter)
- 1:N with face_encodings (photo encodings)

---

### CRIME_DATA Table
```sql
CREATE TABLE crime_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    location VARCHAR(255) NOT NULL COMMENT 'Crime location name',
    type VARCHAR(120) COMMENT 'Crime type: Theft, Robbery, Assault, etc.',
    severity TINYINT DEFAULT 1 COMMENT 'Severity scale 1-5 (1=Low, 5=Critical)',
    date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Incident date/time',
    lat DOUBLE COMMENT 'Latitude for geo-mapping',
    lng DOUBLE COMMENT 'Longitude for geo-mapping',
    description TEXT COMMENT 'Incident details',
    created_by INT,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_location (location),
    INDEX idx_type (type),
    INDEX idx_date (date),
    INDEX idx_severity (severity),
    SPATIAL INDEX idx_geo (POINT(lat, lng))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Relationships**:
- N:1 with users (created_by)
- 1:N with alert_history (alerts)

---

### NOTIFICATION_DEVICES Table
```sql
CREATE TABLE notification_devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) UNIQUE NOT NULL COMMENT 'Firebase FCM token',
    platform VARCHAR(50) COMMENT 'Device platform: iOS, Android, Web',
    user_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_used DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_token (token),
    INDEX idx_user (user_id),
    INDEX idx_platform (platform),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Relationships**:
- N:1 with users (subscriber)
- 1:N with alert_history (recipient)

---

### ALERT_HISTORY Table
```sql
CREATE TABLE alert_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(100) COMMENT 'Type: face_match, risk_alert, status_update, etc.',
    reference VARCHAR(255) COMMENT 'Related entity ID: missing_person_id, crime_id',
    message TEXT COMMENT 'Alert message content',
    recipient_id INT COMMENT 'User who received alert',
    device_id INT COMMENT 'Device that received notification',
    sent_status ENUM('pending', 'sent', 'failed', 'bounced') DEFAULT 'pending',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (device_id) REFERENCES notification_devices(id) ON DELETE SET NULL,
    INDEX idx_alert_type (alert_type),
    INDEX idx_recipient (recipient_id),
    INDEX idx_created (created_on),
    INDEX idx_status (sent_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### FACE_ENCODINGS Table (Optional Optimization)
```sql
CREATE TABLE face_encodings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    person_id INT NOT NULL,
    encoding LONGBLOB COMMENT 'Serialized face embedding (pickle)',
    model_version VARCHAR(50) COMMENT 'Model used: deepface_facenet512, face_recognition, etc.',
    confidence FLOAT COMMENT 'Extraction confidence score',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (person_id) REFERENCES missing_persons(id) ON DELETE CASCADE,
    UNIQUE KEY uk_person_model (person_id, model_version),
    INDEX idx_created (created_on)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Database Indexing Strategy

### Primary Indexes
- **missing_persons.status**: Frequently filtered for "missing" vs "found"
- **missing_persons.date_reported**: Used for sorting recent reports
- **crime_data.location**: Used for location-based analytics
- **crime_data.date**: Used for trend analysis (12-month queries)
- **users.role**: Used for RBAC permission checking
- **alert_history.created_on**: Used for audit trails

### Search Indexes
- **missing_persons.description**: Full-text search for person details
- **crime_data.location**: Prefix search for location filtering

### Spatial Indexes
- **crime_data (lat, lng)**: Geographic queries for heatmaps

---

## Relationships Summary

| From | To | Type | Purpose |
|------|----|----|---------|
| USERS | MISSING_PERSONS | 1:N | Reporter of missing persons |
| USERS | CRIME_DATA | 1:N | Creator of crime reports |
| USERS | NOTIFICATION_DEVICES | 1:N | Device subscriptions |
| MISSING_PERSONS | FACE_ENCODINGS | 1:N | Multiple encodings per person |
| CRIME_DATA | ALERT_HISTORY | 1:N | Alerts triggered by crimes |
| NOTIFICATION_DEVICES | ALERT_HISTORY | 1:N | Device receives alerts |

---

## Database Query Examples

### Analytics Queries

#### Recent Missing Persons (Last 30 Days)
```sql
SELECT COUNT(*) as recent_missing_count
FROM missing_persons
WHERE status = 'missing' 
  AND date_reported >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

#### Crime Hotspots by Location
```sql
SELECT location, 
       COUNT(*) as crime_count,
       AVG(severity) as avg_severity,
       COUNT(DISTINCT type) as unique_types
FROM crime_data
WHERE date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY location
ORDER BY crime_count DESC
LIMIT 10;
```

#### Alert Delivery Rate
```sql
SELECT alert_type,
       sent_status,
       COUNT(*) as count,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY alert_type), 2) as percentage
FROM alert_history
WHERE created_on >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY alert_type, sent_status;
```

#### User Activity
```sql
SELECT u.username, 
       u.role,
       COUNT(DISTINCT mp.id) as missing_reports,
       COUNT(DISTINCT cd.id) as crime_reports,
       MAX(cd.date) as last_activity
FROM users u
LEFT JOIN missing_persons mp ON u.id = mp.reporter_id
LEFT JOIN crime_data cd ON u.id = cd.created_by
GROUP BY u.id
ORDER BY last_activity DESC;
```

---

## Performance Optimization Tips

1. **Partitioning**: Partition alert_history and crime_data by date for faster queries
2. **Archiving**: Move old alerts (>1 year) to archive table
3. **Denormalization**: Consider storing crime stats in summary table for dashboard
4. **Caching**: Cache hotspot analysis (expires every 6 hours)
5. **Connection Pooling**: Use SQLAlchemy pool_size for high-load scenarios

