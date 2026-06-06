"""
Notification registration routes for Firebase Cloud Messaging.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from models.database import db, NotificationDevice
from routes.auth import roles_required
from utils.firebase_utils import notify_test_alert

notifications_bp = Blueprint('notifications', __name__)

def _get_request_payload():
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        return payload
    return request.values or {}


def _resolve_token(payload):
    return (payload.get('device_token') or payload.get('token') or payload.get('deviceToken') or '').strip()


def _resolve_platform(payload):
    return (payload.get('platform') or payload.get('device_platform') or payload.get('devicePlatform') or '').strip()


def _validate_token(token: str):
    if len(token) < 100:
        return jsonify({
            'success': False,
            'error': 'Invalid FCM token'
        }), 400
    return None


@notifications_bp.route('/register', methods=['POST'])
def register_device():
    data = _get_request_payload()
    token = _resolve_token(data)
    platform = _resolve_platform(data)

    if not token:
        current_app.logger.debug('Notification register missing token; payload=%s', data)
        return jsonify({'success': False, 'error': 'device token is required'}), 400
    invalid_token_response = _validate_token(token)
    if invalid_token_response:
        return invalid_token_response

    device = NotificationDevice.query.filter_by(token=token).first()
    if device:
        device.platform = platform or device.platform
        device.updated_on = db.func.now()
    else:
        device = NotificationDevice()
        device.token = token
        device.platform = platform
        db.session.add(device)

    db.session.commit()
    current_app.logger.info('Device registered: %s...', token[:20])
    return jsonify({'success': True, 'message': 'Device registered for notifications'})


@notifications_bp.route('/status', methods=['POST'])
def notification_status():
    data = _get_request_payload()
    token = _resolve_token(data)

    if not token:
        return jsonify({
            'success': True,
            'registered': False
        })

    device = NotificationDevice.query.filter_by(token=token).first()
    return jsonify({
        'success': True,
        'registered': device is not None
    })


@notifications_bp.route('/unregister', methods=['POST'])
def unregister_device():
    data = _get_request_payload()
    token = _resolve_token(data)

    if not token:
        current_app.logger.debug('Notification unregister missing token; payload=%s', data)
        return jsonify({'success': False, 'error': 'device token is required'}), 400
    invalid_token_response = _validate_token(token)
    if invalid_token_response:
        return invalid_token_response

    device = NotificationDevice.query.filter_by(token=token).first()
    if device:
        db.session.delete(device)
        db.session.commit()
        current_app.logger.info('Device removed: %s...', token[:20])

    return jsonify({'success': True, 'message': 'Device unregistered'})


@notifications_bp.route('/test-alert', methods=['POST'])
@roles_required('Admin')
def send_test_alert():
    actor = current_user.username if current_user.is_authenticated else 'Admin'
    sent = notify_test_alert(actor)
    if not sent:
        return jsonify({
            'success': False,
            'error': 'Test alert could not be sent. Check FCM server key and registered devices.'
        }), 400

    current_app.logger.info('Test alert triggered by %s', actor)
    return jsonify({
        'success': True,
        'message': 'Test alert sent successfully.'
    })


@notifications_bp.route('/test-browser', methods=['POST'])
def record_browser_test_alert():
    actor = current_user.username if current_user.is_authenticated else 'User'
    from models.database import AlertHistory

    alert = AlertHistory(
        alert_type='test_alert',
        reference=actor,
        message=f'Browser test notification triggered by {actor}'
    )
    db.session.add(alert)
    db.session.commit()

    current_app.logger.info('Browser test alert recorded by %s', actor)
    return jsonify({
        'success': True,
        'message': 'Browser test notification recorded.'
    })
