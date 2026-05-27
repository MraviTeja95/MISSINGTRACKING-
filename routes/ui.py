"""
UI Routes – serves the HTML frontend pages
"""

from flask import Blueprint, render_template, redirect, url_for, request, current_app, make_response
from flask_login import current_user

ui_bp = Blueprint('ui', __name__)


def _has_admin_or_police_access():
    return current_user.is_authenticated and current_user.role in ('Admin', 'Police')


@ui_bp.route('/')
def home():
    return render_template('index.html')


@ui_bp.route('/report')
def report():
    return render_template('report.html')


@ui_bp.route('/missing-list')
def missing_list():
    return render_template('missing_list.html')


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
    return render_template('face_search.html')


@ui_bp.route('/notifications/settings')
def notification_settings():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))

    firebase_config = {
        'apiKey': current_app.config.get('FIREBASE_API_KEY', ''),
        'authDomain': current_app.config.get('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': current_app.config.get('FIREBASE_PROJECT_ID', ''),
        'messagingSenderId': current_app.config.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': current_app.config.get('FIREBASE_APP_ID', ''),
        'measurementId': current_app.config.get('FIREBASE_MEASUREMENT_ID', '')
    }
    return render_template(
        'notification_settings.html',
        firebase_config=firebase_config,
        firebase_vapid_key=current_app.config.get('FIREBASE_VAPID_KEY', '')
    )


@ui_bp.route('/firebase-messaging-sw.js')
def firebase_messaging_sw():
    firebase_config = {
        'apiKey': current_app.config.get('FIREBASE_API_KEY', ''),
        'authDomain': current_app.config.get('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': current_app.config.get('FIREBASE_PROJECT_ID', ''),
        'messagingSenderId': current_app.config.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': current_app.config.get('FIREBASE_APP_ID', ''),
        'measurementId': current_app.config.get('FIREBASE_MEASUREMENT_ID', '')
    }
    response = make_response(render_template('firebase-messaging-sw.js', firebase_config=firebase_config))
    response.headers['Content-Type'] = 'application/javascript'
    return response
