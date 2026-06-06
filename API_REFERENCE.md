# 📡 API Reference & Postman Collection

## Overview
Complete REST API documentation for TraceNet. All endpoints are organized by module and include request/response examples.

**Base URL**: `http://localhost:5000/api`

---

## Table of Contents
1. Authentication APIs
2. Missing Persons APIs
3. Crime Data APIs
4. AI Features APIs
5. Dashboard APIs
6. Notifications APIs
7. UI Routes

---

## 1. Authentication APIs

### 1.1 User Signup

```
POST /auth/signup
Content-Type: application/json

Request Body:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "Public"  # Options: Public, Police, Admin
}

Response (201 Created):
{
  "success": true,
  "message": "User registered successfully",
  "user_id": 1,
  "role": "Public"
}

Response (400 Bad Request):
{
  "success": false,
  "message": "User already exists"
}
```

### 1.2 User Login

```
POST /auth/login
Content-Type: application/json

Request Body:
{
  "username": "john_doe",
  "password": "SecurePass123"
}

Response (200 OK):
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "Public"
  }
}

Response (401 Unauthorized):
{
  "success": false,
  "message": "Invalid credentials"
}
```

### 1.3 Police Login

```
POST /auth/police-login
Content-Type: application/json

Request Body:
{
  "username": "officer_smith",
  "password": "PolicePass123"
}

Response (200 OK):
{
  "success": true,
  "message": "Police login successful",
  "user": {
    "id": 2,
    "username": "officer_smith",
    "email": "smith@police.gov",
    "role": "Police"
  }
}

Response (403 Forbidden):
{
  "success": false,
  "message": "User is not a police officer"
}
```

### 1.4 User Logout

```
POST /auth/logout

Response (200 OK):
{
  "success": true,
  "message": "Logout successful"
}
```

---

## 2. Missing Persons APIs

### 2.1 Report Missing Person

```
POST /api/missing/add
Content-Type: multipart/form-data

Form Parameters:
  - name (string, required): Person's full name
  - age (integer, optional): Age in years
  - photo (file, required): JPG/PNG image (max 16MB)
  - last_seen (string, required): Last known location
  - description (string, optional): Physical description
  - contact (string, required): Reporter phone/email

Response (201 Created):
{
  "success": true,
  "person_id": 5,
  "message": "Missing person report 5 created successfully",
  "photo_path": "/static/uploads/20260602_103045_john_doe.jpg"
}

Response (400 Bad Request):
{
  "success": false,
  "message": "Missing required fields"
}
```

### 2.2 Get Missing Persons List

```
GET /api/missing/list?status=missing&limit=10&offset=0

Query Parameters:
  - status (string, optional): Filter by "missing" or "found"
  - limit (integer, default: 10): Results per page
  - offset (integer, default: 0): Pagination offset

Response (200 OK):
{
  "success": true,
  "persons": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 28,
      "photo": "/static/uploads/photo1.jpg",
      "last_seen": "MG Road, Bangalore",
      "status": "missing",
      "date_reported": "2026-06-02T10:30:45",
      "contact": "+91 98765 43210"
    },
    {
      "id": 2,
      "name": "Sarah Johnson",
      "age": 15,
      "photo": "/static/uploads/photo2.jpg",
      "last_seen": "Whitefield",
      "status": "found",
      "date_reported": "2026-06-01T02:45:00",
      "contact": "+91 98765 43211"
    }
  ],
  "total": 45,
  "limit": 10,
  "offset": 0
}
```

### 2.3 Get Person Details

```
GET /api/missing/1

Response (200 OK):
{
  "success": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "age": 28,
    "photo": "/static/uploads/photo1.jpg",
    "last_seen": "MG Road, Bangalore",
    "description": "Athletic build, black hair, brown eyes",
    "contact": "+91 98765 43210",
    "status": "missing",
    "date_reported": "2026-06-02T10:30:45"
  }
}

Response (404 Not Found):
{
  "success": false,
  "message": "Person not found"
}
```

### 2.4 Update Person Status

```
PUT /api/missing/1/status
Content-Type: application/json

Request Body:
{
  "status": "found"
}

Response (200 OK):
{
  "success": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "status": "found",
    "date_reported": "2026-06-02T10:30:45"
  },
  "message": "Person status updated to found"
}
```

### 2.5 Delete Person Record

```
DELETE /api/missing/1

Response (200 OK):
{
  "success": true,
  "message": "Person record deleted successfully"
}

Response (404 Not Found):
{
  "success": false,
  "message": "Person not found"
}
```

---

## 3. Crime Data APIs

### 3.1 Add Crime Incident

```
POST /api/crime/add
Content-Type: application/json

Request Body:
{
  "location": "MG Road, Bangalore",
  "type": "Theft",
  "severity": 3,
  "lat": 13.0273,
  "lng": 77.5905,
  "description": "Bag stolen from parking lot"
}

Response (201 Created):
{
  "success": true,
  "crime_id": 12,
  "message": "Crime record created successfully"
}
```

### 3.2 Get Crime List

```
GET /api/crime/list?location=MG Road&limit=20

Query Parameters:
  - location (string, optional): Filter by location
  - limit (integer, default: 20): Results per page
  - offset (integer, default: 0): Pagination offset

Response (200 OK):
{
  "success": true,
  "crimes": [
    {
      "id": 1,
      "location": "MG Road",
      "type": "Theft",
      "severity": 3,
      "date": "2026-06-02T10:30:45",
      "lat": 13.0273,
      "lng": 77.5905,
      "description": "Bag stolen from parking lot",
      "created_by": "officer_smith"
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0
}
```

### 3.3 Get Crime Statistics

```
GET /api/crime/stats

Response (200 OK):
{
  "success": true,
  "stats": {
    "total_crimes": 156,
    "crimes_by_location": {
      "MG Road": 8,
      "Koramangala": 6,
      "Whitefield": 5,
      "Jayanagar": 4,
      "Indiranagar": 3
    },
    "crimes_by_type": {
      "Theft": 45,
      "Robbery": 32,
      "Assault": 22,
      "Cybercrime": 12,
      "Other": 45
    },
    "severity_distribution": {
      "1": 20,
      "2": 35,
      "3": 45,
      "4": 38,
      "5": 18
    }
  }
}
```

### 3.4 Get 12-Month Trends

```
GET /api/crime/trends

Response (200 OK):
{
  "success": true,
  "trends": [
    {
      "month": "June 2025",
      "crimes": 12,
      "missing_persons": 2
    },
    {
      "month": "July 2025",
      "crimes": 14,
      "missing_persons": 3
    },
    ...
    {
      "month": "June 2026",
      "crimes": 18,
      "missing_persons": 4
    }
  ]
}
```

### 3.5 Reseed Demo Data

```
POST /api/crime/reseed

Response (200 OK):
{
  "success": true,
  "message": "Crime data reseeded successfully"
}
```

---

## 4. AI Features APIs

### 4.1 Face Recognition Search

```
POST /api/ai/match-face
Content-Type: multipart/form-data

Form Parameters:
  - image (file, required): JPG/PNG image for matching
  - confidence_threshold (float, optional): Threshold % (default: 70)

Response (200 OK):
{
  "success": true,
  "matches": [
    {
      "person_id": 1,
      "name": "John Doe",
      "confidence": 89.3,
      "age": 28,
      "last_seen": "MG Road, 3 days ago",
      "photo": "/static/uploads/photo1.jpg",
      "status": "missing"
    },
    {
      "person_id": 3,
      "name": "Michael Chen",
      "confidence": 74.8,
      "age": 42,
      "last_seen": "Whitefield, 7 days ago",
      "photo": "/static/uploads/photo3.jpg",
      "status": "missing"
    }
  ],
  "search_time_ms": 1230
}

Response (400 Bad Request):
{
  "success": false,
  "message": "No image file provided"
}
```

### 4.2 Predict Risk Areas

```
GET /api/ai/predict-risk

Response (200 OK):
{
  "success": true,
  "risk_predictions": {
    "high_risk": ["MG Road", "Koramangala"],
    "medium_risk": ["Whitefield", "Jayanagar"],
    "low_risk": ["Indiranagar", "Hebbal"],
    "predictions": [
      {
        "location": "MG Road",
        "predicted_risk": "High",
        "confidence": 0.87,
        "incident_count": 8,
        "avg_severity": 3.5
      }
    ]
  }
}
```

### 4.3 Rebuild Face Encodings

```
POST /api/ai/rebuild-face-encodings

Response (200 OK):
{
  "success": true,
  "processed": 45,
  "failed": 0,
  "message": "Rebuilt 45 face encodings successfully"
}
```

---

## 5. Dashboard APIs

### 5.1 Get Dashboard Summary

```
GET /api/dashboard/summary

Response (200 OK):
{
  "success": true,
  "summary": {
    "total_missing": 45,
    "total_found": 12,
    "total_crimes": 156,
    "recent_reports": 3,
    "crimes_by_location": {
      "MG Road": 8,
      "Koramangala": 6,
      "Whitefield": 5
    },
    "crimes_by_type": {
      "Theft": 45,
      "Robbery": 32,
      "Assault": 22
    },
    "trends_12_months": [
      {"month": "June 2026", "crimes": 18, "missing": 4}
    ]
  }
}
```

### 5.2 Get Crime Density Heatmap Data

```
GET /api/dashboard/crime-density

Response (200 OK):
{
  "success": true,
  "heatmap_data": [
    {
      "location": "MG Road",
      "lat": 13.0273,
      "lng": 77.5905,
      "crime_density": 8,
      "risk_level": "High",
      "color": "red"
    },
    {
      "location": "Koramangala",
      "lat": 12.9355,
      "lng": 77.6245,
      "crime_density": 6,
      "risk_level": "Medium",
      "color": "orange"
    }
  ]
}
```

---

## 6. Notifications APIs

### 6.1 Register Device Token

```
POST /api/notifications/register
Content-Type: application/json

Request Body:
{
  "token": "device_fcm_token_here",
  "platform": "Android"  # Android, iOS, Web
}

Response (201 Created):
{
  "success": true,
  "device_id": 5,
  "message": "Device registered successfully"
}
```

### 6.2 Unregister Device Token

```
POST /api/notifications/unregister
Content-Type: application/json

Request Body:
{
  "token": "device_fcm_token_here"
}

Response (200 OK):
{
  "success": true,
  "message": "Device unregistered successfully"
}
```

---

## 7. UI Routes (HTML Pages)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page |
| `/login` | GET | Login page |
| `/signup` | GET | Signup page |
| `/report` | GET | Report missing person form |
| `/missing-list` | GET | View all missing persons |
| `/dashboard` | GET | Police/Admin dashboard |
| `/face-search` | GET | AI face recognition tool |
| `/notifications/settings` | GET | Notification preferences |
| `/unauthorized` | GET | 403 error page |
| `/logout` | POST | Logout user |

---

## Postman Collection JSON

Save as `TraceNet_API.postman_collection.json`:

```json
{
  "info": {
    "name": "TraceNet API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Signup",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/auth/signup",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["auth", "signup"]
            },
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"test_user\",\n  \"email\": \"test@example.com\",\n  \"password\": \"TestPass123\",\n  \"role\": \"Public\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/auth/login",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["auth", "login"]
            },
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"test_user\",\n  \"password\": \"TestPass123\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Missing Persons",
      "item": [
        {
          "name": "Add Missing Person",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/missing/add",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "missing", "add"]
            },
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "name",
                  "value": "John Doe"
                },
                {
                  "key": "age",
                  "value": "28"
                },
                {
                  "key": "last_seen",
                  "value": "MG Road, Bangalore"
                },
                {
                  "key": "photo",
                  "type": "file",
                  "src": "/path/to/photo.jpg"
                }
              ]
            }
          }
        },
        {
          "name": "Get Missing Persons List",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/missing/list?status=missing&limit=10",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "missing", "list"],
              "query": [
                {
                  "key": "status",
                  "value": "missing"
                },
                {
                  "key": "limit",
                  "value": "10"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "name": "Crime Data",
      "item": [
        {
          "name": "Add Crime",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/crime/add",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "crime", "add"]
            },
            "body": {
              "mode": "raw",
              "raw": "{\n  \"location\": \"MG Road\",\n  \"type\": \"Theft\",\n  \"severity\": 3,\n  \"lat\": 13.0273,\n  \"lng\": 77.5905\n}"
            }
          }
        },
        {
          "name": "Get Crime Stats",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/crime/stats",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "crime", "stats"]
            }
          }
        }
      ]
    },
    {
      "name": "AI Features",
      "item": [
        {
          "name": "Face Recognition Search",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/ai/match-face",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "ai", "match-face"]
            },
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "image",
                  "type": "file",
                  "src": "/path/to/query_image.jpg"
                },
                {
                  "key": "confidence_threshold",
                  "value": "70"
                }
              ]
            }
          }
        },
        {
          "name": "Predict Risk Areas",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/ai/predict-risk",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "ai", "predict-risk"]
            }
          }
        }
      ]
    },
    {
      "name": "Dashboard",
      "item": [
        {
          "name": "Get Summary",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/dashboard/summary",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "dashboard", "summary"]
            }
          }
        },
        {
          "name": "Get Crime Density",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/api/dashboard/crime-density",
              "protocol": "http",
              "host": ["localhost"],
              "port": "5000",
              "path": ["api", "dashboard", "crime-density"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000",
      "type": "string"
    }
  ]
}
```

---

## HTTP Status Codes Reference

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request successful |
| 201 | Created | New resource created |
| 400 | Bad Request | Missing/invalid parameters |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error |

---

## Authentication Headers

All requests (except `/auth/*`) should include session cookies:
```
Cookie: session=eyJ...
```

Or for API token (if implemented):
```
Authorization: Bearer <token>
```

---

