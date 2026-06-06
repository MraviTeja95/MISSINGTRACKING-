"""
AI Feature Routes
  POST /api/ai/match-face     – Upload an image, compare against all stored faces
  GET  /api/ai/predict-risk   – Predict high-risk crime areas using sklearn
  GET  /api/ai/hotspots       – Top crime hotspots with risk scores
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from utils.helpers import allowed_file
import time

ai_bp = Blueprint('ai', __name__)


# ── Face Matching ──────────────────────────────────────────────────────────────

@ai_bp.route('/match-face', methods=['POST'])
def match_face():
    """
    Upload an image and find the best matching missing person.
    Returns match percentage and person details if a match is found.
    """
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No photo provided'}), 400

    file = request.files['photo']
    if not file or not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400

    try:
        # Save the query image temporarily
        filename    = secure_filename(file.filename)
        base, ext   = os.path.splitext(filename)
        temp_name   = f"query_{int(time.time())}{ext}"
        temp_path   = os.path.join(current_app.config['UPLOAD_FOLDER'], temp_name)
        file.save(temp_path)

        confidence_threshold = request.form.get('confidence_threshold', None)
        try:
            confidence_threshold = float(confidence_threshold) if confidence_threshold is not None else None
        except ValueError:
            confidence_threshold = None

        # Run face comparison
        from utils.face_utils import find_matching_person
        result = find_matching_person(temp_path, confidence_threshold=confidence_threshold)

        try:
            from utils.firebase_utils import notify_face_match
            if result.get('match_found'):
                notify_face_match(result)
        except Exception as e:
            current_app.logger.warning(f'Face match notification failed: {e}')

        # Clean up temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass

        response = {
            'success': True,
            'result': result,
            'person_id': result.get('person_id'),
            'match_percent': result.get('match_percent'),
            'confidence_threshold': result.get('confidence_threshold')
        }
        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f"Face match error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/rebuild-face-encodings', methods=['POST'])
def rebuild_face_encodings():
    """
    Rebuild face encodings for all missing persons in the database.
    This is useful when face_recognition library or models are updated.
    Returns the count of successfully encoded persons.
    """
    try:
        from utils.face_utils import rebuild_all_encodings
        count = rebuild_all_encodings()
        return jsonify({
            'success': True,
            'message': f'Successfully rebuilt {count} face encodings',
            'encoded_count': count
        })
    except Exception as e:
        current_app.logger.error(f"Rebuild encodings error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Crime Pattern Prediction ───────────────────────────────────────────────────

@ai_bp.route('/predict-risk', methods=['GET'])
def predict_risk():
    """
    Use a trained Random Forest model to classify locations as high/medium/low risk.
    Returns a list of locations with their predicted risk labels and scores.
    """
    try:
        from utils.ml_utils import predict_risk_areas
        predictions = predict_risk_areas()
        try:
            from utils.firebase_utils import notify_high_risk_locations
            notify_high_risk_locations(predictions)
        except Exception as e:
            current_app.logger.warning(f'High risk notification failed: {e}')
        return jsonify({'success': True, 'predictions': predictions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _parse_datetime_payload(data):
    date_time = data.get('datetime') or data.get('timestamp')
    if date_time:
        try:
            return datetime.fromisoformat(date_time)
        except ValueError:
            pass

        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_time, fmt)
            except ValueError:
                continue

    date_str = data.get('date')
    time_str = data.get('time')
    if date_str and time_str:
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                return datetime.strptime(f"{date_str} {time_str}", fmt)
            except ValueError:
                continue

    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass

    raise ValueError('Invalid or missing datetime. Use "datetime", "timestamp", or "date"/"time".')


@ai_bp.route('/predict-crime', methods=['POST'])
def predict_crime():
    """
    Predict the probability of a crime occurring for a specific location and time.
    Input JSON should include:
      - location
      - datetime (ISO string) or date + time
    """
    try:
        data = request.get_json(force=True) or {}
        location = (data.get('location') or '').strip()
        if not location:
            return jsonify({'success': False, 'error': 'Location is required'}), 400

        try:
            query_dt = _parse_datetime_payload(data)
        except ValueError as err:
            return jsonify({'success': False, 'error': str(err)}), 400

        from utils.ml_utils import predict_crime_probability
        prediction = predict_crime_probability(location, query_dt)
        if prediction is None:
            return jsonify({'success': False, 'error': 'Not enough historical crime data to train the model'}), 400

        try:
            from utils.firebase_utils import notify_high_crime_probability
            notify_high_crime_probability(location, query_dt, prediction)
        except Exception as e:
            current_app.logger.warning(f'Crime probability notification failed: {e}')

        return jsonify({'success': True, 'prediction': prediction})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/hotspots', methods=['GET'])
def crime_hotspots():
    """
    Return top crime hotspots enriched with:
    - Total incidents
    - Most common crime type
    - Average severity
    - Risk level (from ML model)
    """
    try:
        from utils.ml_utils import get_hotspot_analysis
        hotspots = get_hotspot_analysis()
        return jsonify({'success': True, 'hotspots': hotspots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/rebuild-encodings', methods=['POST'])
def rebuild_encodings():
    """Force-rebuild all face encodings from stored photos (admin use)."""
    try:
        from utils.face_utils import rebuild_all_encodings
        count = rebuild_all_encodings()
        return jsonify({'success': True, 'message': f'Rebuilt encodings for {count} persons'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
