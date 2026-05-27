"""
Notification registration routes for Firebase Cloud Messaging.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Blueprint, request, jsonify, current_app
from models.database import db, NotificationDevice

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


@notifications_bp.route('/register', methods=['POST'])
def register_device():
    data = _get_request_payload()
    token = _resolve_token(data)
    platform = _resolve_platform(data)

    if not token:
        current_app.logger.debug('Notification register missing token; payload=%s', data)
        return jsonify({'success': False, 'error': 'device token is required'}), 400

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
    return jsonify({'success': True, 'message': 'Device registered for notifications'})


@notifications_bp.route('/unregister', methods=['POST'])
def unregister_device():
    data = _get_request_payload()
    token = _resolve_token(data)

    if not token:
        current_app.logger.debug('Notification unregister missing token; payload=%s', data)
        return jsonify({'success': False, 'error': 'device token is required'}), 400

    device = NotificationDevice.query.filter_by(token=token).first()
    if device:
        db.session.delete(device)
        db.session.commit()

    return jsonify({'success': True, 'message': 'Device unregistered'})
