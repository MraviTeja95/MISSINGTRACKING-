"""
UI Routes – serves the HTML frontend pages
"""

import json

from flask import Blueprint, render_template, redirect, url_for, request, current_app, make_response
from flask_login import current_user
from models.database import AlertHistory

ui_bp = Blueprint('ui', __name__)


def _has_admin_or_police_access():
    return current_user.is_authenticated and current_user.role in ('Admin', 'Police')


def _firebase_web_config():
    return {
        'apiKey': current_app.config.get('FIREBASE_API_KEY', ''),
        'authDomain': current_app.config.get('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': current_app.config.get('FIREBASE_PROJECT_ID', ''),
        'storageBucket': current_app.config.get('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': current_app.config.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': current_app.config.get('FIREBASE_APP_ID', ''),
        'measurementId': current_app.config.get('FIREBASE_MEASUREMENT_ID', '')
    }


def _recent_notification_history(limit: int = 5):
    label_map = {
        'face_match': 'Face Match Alert',
        'high_crime': 'Crime Risk Alert',
        'high_crime_prediction': 'Crime Risk Alert',
        'crime_probability': 'Crime Probability Alert',
        'test_alert': 'Test Notification'
    }
    alerts = AlertHistory.query.order_by(AlertHistory.created_on.desc()).limit(limit).all()
    return [
        {
            'title': label_map.get(alert.alert_type, (alert.alert_type or 'Notification').replace('_', ' ').title()),
            'message': alert.message or 'Notification event recorded.',
            'created_on': alert.created_on
        }
        for alert in alerts
    ]


@ui_bp.route('/')
def home():
    return render_template('index.html')


@ui_bp.route('/report')
def report():
    return render_template('report.html')


@ui_bp.route('/missing-list')
def missing_list():
    return render_template(
        'missing_list.html',
        is_police=_has_admin_or_police_access()
    )


@ui_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    if current_user.role not in ('Admin', 'Police'):
        return render_template('unauthorized.html'), 403
    return render_template('dashboard.html')


@ui_bp.route('/face-search')
def face_search():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    if current_user.role not in ('Admin', 'Police'):
        return render_template('unauthorized.html'), 403
    return render_template('face_search.html',
                           face_match_confidence_threshold=int(current_app.config.get('FACE_MATCH_CONFIDENCE_THRESHOLD', 70)))


@ui_bp.route('/notifications/settings')
def notification_settings():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))

    return render_template(
        'notification_settings.html',
        firebase_config=_firebase_web_config(),
        firebase_vapid_key=current_app.config.get('FIREBASE_VAPID_KEY', ''),
        recent_notifications=_recent_notification_history()
    )


@ui_bp.route('/firebase-config-sw.js')
def firebase_config_sw():
    response = make_response(
        f"self.__TRACE_NET_FIREBASE_CONFIG__ = {json.dumps(_firebase_web_config())};"
    )
    response.headers['Content-Type'] = 'application/javascript'
    return response
