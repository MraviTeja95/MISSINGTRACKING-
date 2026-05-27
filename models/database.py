"""
Database Models
- MissingPerson  : stores missing person reports
- CrimeData      : stores crime incident records
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class MissingPerson(db.Model):
    __tablename__ = 'missing_persons'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    age         = db.Column(db.Integer, nullable=False)
    photo       = db.Column(db.String(255), nullable=True)   # filename stored in /static/uploads/
    last_seen   = db.Column(db.String(255), nullable=False)  # free-text location
    description = db.Column(db.Text, nullable=True)
    contact     = db.Column(db.String(120), nullable=True)   # reporter contact
    status      = db.Column(db.String(30), default='missing')# missing | found
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'name':         self.name,
            'age':          self.age,
            'photo':        f'/static/uploads/{self.photo}' if self.photo else None,
            'last_seen':    self.last_seen,
            'description':  self.description,
            'contact':      self.contact,
            'status':       self.status,
            'date_reported': self.date_reported.strftime('%Y-%m-%d %H:%M')
        }


class CrimeData(db.Model):
    __tablename__ = 'crime_data'

    id       = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    type     = db.Column(db.String(120), nullable=False)    # robbery, assault, etc.
    severity = db.Column(db.Integer, default=1)             # 1-5 scale
    date     = db.Column(db.DateTime, default=datetime.utcnow)
    lat      = db.Column(db.Float, nullable=True)
    lng      = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id':       self.id,
            'location': self.location,
            'type':     self.type,
            'severity': self.severity,
            'date':     self.date.strftime('%Y-%m-%d'),
            'lat':      self.lat,
            'lng':      self.lng
        }


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Public')
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == 'Admin'

    def is_police(self) -> bool:
        return self.role == 'Police'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_on': self.created_on.strftime('%Y-%m-%d %H:%M')
        }


class NotificationDevice(db.Model):
    __tablename__ = 'notification_devices'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertHistory(db.Model):
    __tablename__ = 'alert_history'

    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
