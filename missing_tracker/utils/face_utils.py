"""
Face Recognition Utilities
Uses DeepFace (primary) for accurate face matching.
Falls back to a demo/mock result if no AI library is available.

Workflow:
  - update_face_encodings(): called when a missing person is reported,
    extracts a 128-d (or 512-d) face embedding and stores it in a pickle file.
  - find_matching_person(): uploads a query image, encodes the face,
    and compares it against all stored embeddings using cosine similarity.
"""

import os
import pickle
import numpy as np
from flask import current_app

# ── Detect available AI libraries ───────────────────────────────────────────
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

DEEPFACE_AVAILABLE = False
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    pass

FACE_RECOGNITION_AVAILABLE = False
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    pass

# Choose the best available engine
if DEEPFACE_AVAILABLE:
    FACE_ENGINE = 'deepface'
elif FACE_RECOGNITION_AVAILABLE:
    FACE_ENGINE = 'face_recognition'
else:
    FACE_ENGINE = 'mock'

# DeepFace model config — Facenet512 is accurate and reasonably fast
_DEEPFACE_MODEL = 'Facenet512'
_DEEPFACE_DETECTOR = 'opencv'


# ── Encodings storage ───────────────────────────────────────────────────────

def _get_encodings_file():
    """Return path to the face encodings pickle file."""
    return current_app.config.get('FACE_ENCODINGS_FILE',
           os.path.join(os.path.dirname(__file__), 'face_encodings.pkl'))


def _load_encodings():
    """Load stored face encodings dict: {person_id: numpy_array}"""
    path = _get_encodings_file()
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}


def _save_encodings(encodings_dict):
    """Persist the face encodings dict to disk."""
    path = _get_encodings_file()
    with open(path, 'wb') as f:
        pickle.dump(encodings_dict, f)


# ── Face embedding extraction ──────────────────────────────────────────────

def _extract_embedding_deepface(image_path: str):
    """Extract face embedding using DeepFace."""
    try:
        results = DeepFace.represent(
            img_path=image_path,
            model_name=_DEEPFACE_MODEL,
            detector_backend=_DEEPFACE_DETECTOR,
            enforce_detection=True,  # Stricter: require actual face detection
            align=True
        )
        if results and len(results) > 0:
            embedding = results[0].get('embedding')
            if embedding is not None:
                return np.array(embedding, dtype=np.float32)
    except Exception as e:
        current_app.logger.warning(f"DeepFace embedding error: {e}")
    return None


def _extract_embedding_face_recognition(image_path: str):
    """Extract face embedding using face_recognition library."""
    try:
        if OPENCV_AVAILABLE:
            image = cv2.imread(image_path)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image = face_recognition.load_image_file(image_path)
        else:
            image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)
        if encodings:
            return np.array(encodings[0], dtype=np.float32)
    except Exception as e:
        current_app.logger.warning(f"face_recognition embedding error: {e}")
    return None


def _extract_embedding(image_path: str):
    """Extract face embedding using the best available engine."""
    if FACE_ENGINE == 'deepface':
        return _extract_embedding_deepface(image_path)
    elif FACE_ENGINE == 'face_recognition':
        return _extract_embedding_face_recognition(image_path)
    return None


# ── Similarity computation ─────────────────────────────────────────────────

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two embedding vectors (0-100 scale)."""
    try:
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        similarity = dot / (norm_a * norm_b)
        # Clamp to [0, 1] range for face embeddings
        similarity = float(np.clip(similarity, -1.0, 1.0))
        # Convert to percentage: (similarity + 1) / 2 → [0, 1] then * 100
        # This ensures that -1 → 0%, 0 → 50%, 1 → 100%
        percentage = ((similarity + 1.0) / 2.0) * 100.0
        return float(round(percentage, 1))
    except Exception:
        return 0.0


# ── Public API ──────────────────────────────────────────────────────────────

def update_face_encodings(image_path: str, int_id: int):
    """
    Compute the face embedding for `image_path` and store it
    under the given person `int_id` in the encodings file.
    """
    if FACE_ENGINE == 'mock':
        return

    if not os.path.exists(image_path):
        return

    try:
        embedding = _extract_embedding(image_path)
        if embedding is not None:
            enc_dict = _load_encodings()
            enc_dict[int_id] = embedding
            _save_encodings(enc_dict)
            current_app.logger.info(
                f"Face encoding saved for person {int_id} using {FACE_ENGINE} "
                f"(dim={len(embedding)})"
            )
        else:
            current_app.logger.warning(
                f"No face detected in {image_path} for person {int_id}"
            )
    except Exception as e:
        current_app.logger.warning(f"Face encoding error for {image_path}: {e}")


def find_matching_person(query_image_path: str, confidence_threshold: float = None) -> dict:
    """
    Compare query image against all stored face embeddings.
    Uses stricter matching to reduce false positives.

    Returns:
        {
          'match_found'         : bool,
          'person_id'           : int | None,
          'match_percent'       : float,
          'confidence_threshold': float,
          'person'              : dict | None,
          'engine'              : str
        }
    """
    if FACE_ENGINE == 'mock':
        return _mock_face_result()

    try:
        # Extract query face embedding
        query_embedding = _extract_embedding(query_image_path)

        if query_embedding is None:
            return {
                'match_found': False, 'person_id': None,
                'match_percent': 0, 'person': None,
                'confidence_threshold': confidence_threshold,
                'engine': FACE_ENGINE,
                'message': 'No face detected in the uploaded image. Please upload a clear photo with a visible face.'
            }

        # Load stored encodings
        enc_dict = _load_encodings()

        if not enc_dict:
            return {
                'match_found': False, 'person_id': None,
                'match_percent': 0, 'person': None,
                'confidence_threshold': confidence_threshold,
                'engine': FACE_ENGINE,
                'message': 'No face encodings in database. Report missing persons first to build the database.'
            }

        # Compare against all stored faces
        best_id = None
        best_score = 0.0
        all_scores = {}
        valid_comparisons = 0

        for pid, stored_embedding in enc_dict.items():
            # Ensure embeddings have same dimensionality
            if len(query_embedding) != len(stored_embedding):
                current_app.logger.warning(
                    f"Dimension mismatch for person {pid}: "
                    f"query={len(query_embedding)}, stored={len(stored_embedding)}"
                )
                continue
            
            score = _cosine_similarity(query_embedding, stored_embedding)
            all_scores[pid] = score
            valid_comparisons += 1
            
            # Only consider scores above 40% to reduce false positives
            if score >= 40.0 and score > best_score:
                best_score = score
                best_id = pid

        # Determine match threshold
        if confidence_threshold is None:
            confidence_threshold = current_app.config.get(
                'FACE_MATCH_CONFIDENCE_THRESHOLD', 70.0
            )

        # Higher default threshold for better accuracy
        confidence_threshold = max(confidence_threshold, 70.0)
        match_found = best_score >= confidence_threshold

        # Fetch person data from database
        person_data = None
        if best_id is not None:
            from models.database import MissingPerson
            person = MissingPerson.query.get(best_id)
            if person:
                person_data = person.to_dict()

        current_app.logger.info(
            f"Face match: best_score={best_score}, threshold={confidence_threshold}, "
            f"match_found={match_found}, valid_comparisons={valid_comparisons}"
        )

        return {
            'match_found':          bool(match_found),
            'person_id':            int(best_id) if best_id is not None else None,
            'match_percent':        float(best_score),
            'confidence_threshold': float(confidence_threshold),
            'person':               person_data,
            'engine':               FACE_ENGINE,
            'total_compared':       int(valid_comparisons)
        }

    except Exception as e:
        current_app.logger.error(f"Face match error: {e}", exc_info=True)
        return {'match_found': False, 'error': str(e), 'engine': FACE_ENGINE}


def rebuild_all_encodings() -> int:
    """Rebuild face encodings for all persons in the database."""
    if FACE_ENGINE == 'mock':
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
            embedding = _extract_embedding(img_path)
            if embedding is not None:
                enc_dict[person.id] = embedding
                count += 1
                current_app.logger.info(
                    f"Encoded person {person.id} ({person.name})"
                )
        except Exception as e:
            current_app.logger.warning(
                f"Failed to encode person {person.id}: {e}"
            )

    _save_encodings(enc_dict)
    current_app.logger.info(
        f"Rebuilt {count} face encodings using {FACE_ENGINE}"
    )
    return count


def _mock_face_result() -> dict:
    """
    Demo result returned when no AI library is installed.
    Simulates a realistic match for demonstration purposes.
    """
    import random
    from models.database import MissingPerson

    persons = MissingPerson.query.filter_by(status='missing').all()
    if persons:
        person = random.choice(persons)
        pct = round(random.uniform(72.0, 94.0), 1)
        return {
            'match_found':   True,
            'person_id':     person.id,
            'match_percent': pct,
            'person':        person.to_dict(),
            'engine':        'mock',
            'note':          'Demo mode – install deepface for real AI matching: pip install deepface'
        }
    return {
        'match_found': False, 'person_id': None,
        'match_percent': 0, 'person': None,
        'engine': 'mock',
        'note': 'Demo mode – no records in database'
    }
