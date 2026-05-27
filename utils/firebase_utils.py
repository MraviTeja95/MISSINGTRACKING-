"""
Firebase notification helpers for TraceNet.
Sends push notifications using Firebase Cloud Messaging (FCM) and stores device tokens.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from flask import current_app


def _get_fcm_key():
    return current_app.config.get('FCM_SERVER_KEY', '')


def _get_fcm_url():
    return 'https://fcm.googleapis.com/fcm/send'


def _send_fcm_batch(title: str, body: str, data: dict, tokens: list[str]) -> bool:
    key = _get_fcm_key()
    if not key or not tokens:
        current_app.logger.debug('FCM key missing or no tokens available')
        return False

    headers = {
        'Authorization': f'key={key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'registration_ids': tokens,
        'notification': {
            'title': title,
            'body': body
        },
        'data': data or {}
    }

    request_data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(_get_fcm_url(), data=request_data, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_data = response.read().decode('utf-8')
            current_app.logger.info(f'FCM response: {response_data}')
            return True
    except urllib.error.HTTPError as exc:
        error_text = exc.read().decode('utf-8') if exc.fp else str(exc)
        current_app.logger.error(f'FCM HTTP error: {exc.code} {error_text}')
    except Exception as exc:
        current_app.logger.error(f'FCM send failed: {exc}')
    return False


def _chunk_tokens(tokens: list[str], chunk_size: int = 1000):
    for i in range(0, len(tokens), chunk_size):
        yield tokens[i:i + chunk_size]


def _get_registered_tokens():
    from models.database import NotificationDevice
    return [row.token for row in NotificationDevice.query.all()]


def _send_notification(title: str, body: str, data: dict | None = None) -> bool:
    tokens = _get_registered_tokens()
    if not tokens:
        current_app.logger.info('No registered notification tokens to send')
        return False

    success = False
    for chunk in _chunk_tokens(tokens):
        sent = _send_fcm_batch(title, body, data or {}, chunk)
        success = success or sent
    return success


def _has_recent_alert(alert_type: str, reference: str, window_hours: int = 6) -> bool:
    from models.database import AlertHistory
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)
    return AlertHistory.query.filter(
        AlertHistory.alert_type == alert_type,
        AlertHistory.reference == reference,
        AlertHistory.created_on >= cutoff
    ).first() is not None


def _record_alert(alert_type: str, reference: str, message: str) -> None:
    from models.database import AlertHistory, db

    alert = AlertHistory(alert_type=alert_type, reference=reference, message=message)
    db.session.add(alert)
    db.session.commit()


def notify_face_match(result: dict) -> bool:
    if not result.get('match_found') or not result.get('person'):
        return False

    person = result['person']
    title = 'Face Match Alert'
    body = f"Face match found for {person.get('name', 'Unknown')} ({result.get('match_percent', 0)}%)"
    data = {
        'type': 'face_match',
        'person_id': person.get('id'),
        'confidence': result.get('match_percent'),
    }

    sent = _send_notification(title, body, data)
    if sent:
        _record_alert('face_match', str(person.get('id', 'unknown')), body)
    return sent


def notify_high_risk_locations(predictions: list[dict]) -> bool:
    high_risk = [p for p in predictions if p.get('risk_score') == 2]
    if not high_risk:
        return False

    pending = []
    for place in high_risk:
        ref = place.get('location') or 'unknown'
        if not _has_recent_alert('high_crime', ref, current_app.config.get('NOTIFICATION_ALERT_WINDOW_HOURS', 6)):
            pending.append(place)

    if not pending:
        return False

    top_locations = ', '.join([place.get('location') for place in pending[:3]])
    title = 'High Crime Alert'
    body = f'High crime risk detected in {top_locations}'
    data = {
        'type': 'high_crime_prediction',
        'locations': [place.get('location') for place in pending]
    }

    sent = _send_notification(title, body, data)
    if sent:
        for place in pending:
            _record_alert('high_crime', place.get('location') or 'unknown', f"High risk at {place.get('location')}")
    return sent


def notify_high_crime_probability(location: str, query_time, prediction: dict) -> bool:
    threshold = current_app.config.get('CRIME_ALERT_PROBABILITY_THRESHOLD', 70.0)
    if prediction.get('probability', 0) < threshold:
        return False

    ref = f"{location}:{query_time.strftime('%Y-%m-%dT%H:%M')}"
    if _has_recent_alert('crime_probability', ref, current_app.config.get('NOTIFICATION_ALERT_WINDOW_HOURS', 6)):
        return False

    title = 'Crime Probability Alert'
    body = f"High crime probability at {location}: {prediction.get('probability')}%"
    data = {
        'type': 'crime_probability',
        'location': location,
        'datetime': query_time.strftime('%Y-%m-%d %H:%M'),
        'probability': prediction.get('probability')
    }

    sent = _send_notification(title, body, data)
    if sent:
        _record_alert('crime_probability', ref, body)
    return sent
