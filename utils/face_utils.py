"""
Face Recognition Utilities
Uses the `face_recognition` library (built on dlib) to:
  - Encode faces from uploaded photos
  - Compare a query image against all stored encodings
  - Return the best match with a similarity percentage
"""

import os
import pickle
import numpy as np
from flask import current_app

# ── Graceful fallback if optional libraries are not installed ───────────────
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


ENCODINGS_FILE = None  # Set lazily from app context


def _get_encodings_file():
    """Return path to the face encodings pickle file."""
    return current_app.config.get('FACE_ENCODINGS_FILE',
           os.path.join(os.path.dirname(__file__), 'face_encodings.pkl'))


def _load_encodings():
    """Load stored face encodings dict: {person_id: encoding}"""
    path = _get_encodings_file()
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return {}


def _save_encodings(encodings_dict):
    """Persist the face encodings dict to disk."""
    path = _get_encodings_file()
    with open(path, 'wb') as f:
        pickle.dump(encodings_dict, f)


def _load_rgb_image(image_path: str):
    """Load an image as RGB using OpenCV if available, otherwise fallback."""
    if OPENCV_AVAILABLE:
        image = cv2.imread(image_path)
        if image is not None:
            try:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception:
                pass
    return face_recognition.load_image_file(image_path)


def update_face_encodings(image_path: str, int_id: int):
    """
    Compute the face encoding for `image_path` and store it
    under the given person `int_id` in the encodings file.
    If `face_recognition` is not available, this is a no-op.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return

    if not os.path.exists(image_path):
        return

    try:
        image = _load_rgb_image(image_path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            return  # No face detected in image

        enc_dict = _load_encodings()
        enc_dict[int_id] = encodings[0]   # Store first detected face
        _save_encodings(enc_dict)
    except Exception as e:
        current_app.logger.warning(f"face encoding error for {image_path}: {e}")


def _distance_to_match_percent(distance: float, threshold: float) -> float:
    """Convert face distance into a confidence percentage."""
    if distance <= 0:
        return 100.0

    if threshold <= 0:
        threshold = 0.6

    ratio = min(1.0, distance / threshold)
    score = max(0.0, (1.0 - ratio * ratio) * 100.0)
    return round(score, 1)


def find_matching_person(query_image_path: str, confidence_threshold: float = None) -> dict:
    """
    Compare query image against all stored face encodings.

    Returns:
        {
          'match_found'         : bool,
          'person_id'           : int | None,
          'match_percent'       : float,
          'confidence_threshold': float,
          'person'              : dict | None   (from DB)
        }

    Falls back to a mock result if face_recognition is unavailable.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return _mock_face_result()

    try:
        query_image = _load_rgb_image(query_image_path)
        query_encodings = face_recognition.face_encodings(query_image)

        if not query_encodings:
            return {'match_found': False, 'person_id': None,
                    'match_percent': 0, 'person': None,
                    'confidence_threshold': confidence_threshold,
                    'message': 'No face detected in the uploaded image'}

        query_enc = query_encodings[0]
        enc_dict = _load_encodings()

        if not enc_dict:
            return {'match_found': False, 'person_id': None,
                    'match_percent': 0, 'person': None,
                    'confidence_threshold': confidence_threshold,
                    'message': 'No stored face encodings found'}

        best_id = None
        best_dist = float('inf')

        for pid, stored_enc in enc_dict.items():
            dist = face_recognition.face_distance([stored_enc], query_enc)[0]
            if dist < best_dist:
                best_dist = dist
                best_id = pid

        threshold = current_app.config.get('FACE_MATCH_THRESHOLD', 0.6)
        match_percent = _distance_to_match_percent(best_dist, threshold)

        if confidence_threshold is None:
            confidence_threshold = current_app.config.get('FACE_MATCH_CONFIDENCE_THRESHOLD', 70.0)

        match_found = match_percent >= confidence_threshold

        person_data = None
        if best_id is not None:
            from models.database import MissingPerson
            person = MissingPerson.query.get(best_id)
            if person:
                person_data = person.to_dict()

        return {
            'match_found':         match_found,
            'person_id':           best_id,
            'match_percent':       match_percent,
            'confidence_threshold': confidence_threshold,
            'distance':            round(float(best_dist), 4),
            'person':              person_data
        }

    except Exception as e:
        current_app.logger.error(f"Face match error: {e}")
        return {'match_found': False, 'error': str(e)}


def rebuild_all_encodings() -> int:
    """Rebuild face encodings for all persons in the database."""
    if not FACE_RECOGNITION_AVAILABLE:
        return 0

    from models.database import MissingPerson
    upload_folder = current_app.config['UPLOAD_FOLDER']
    enc_dict = {}
    count = 0

    for person in MissingPerson.query.all():
        if not person.photo:
            continue
        img_path = os.path.join(upload_folder, person.photo)
        if not os.path.exists(img_path):
            continue
        try:
            image = _load_rgb_image(img_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                enc_dict[person.id] = encodings[0]
                count += 1
        except Exception:
            pass

    _save_encodings(enc_dict)
    return count


def _mock_face_result() -> dict:
    """
    Demo result returned when face_recognition library is not installed.
    Simulates a realistic match for demonstration purposes.
    """
    import random
    from models.database import MissingPerson

    persons = MissingPerson.query.filter_by(status='missing').all()
    if persons:
        person = random.choice(persons)
        pct    = round(random.uniform(72.0, 94.0), 1)
        return {
            'match_found':   True,
            'person_id':     person.id,
            'match_percent': pct,
            'person':        person.to_dict(),
            'note':          'Demo mode – install face_recognition for real matching'
        }
    return {'match_found': False, 'person_id': None, 'match_percent': 0, 'person': None,
            'note': 'Demo mode – no records in database'}
