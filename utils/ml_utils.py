"""
ML Utilities – Crime Pattern Analysis
Uses scikit-learn to:
  - Train a Random Forest classifier on historical crime data
  - Predict risk levels (High / Medium / Low) per location
  - Identify top hotspots
"""

import os
import pickle
import numpy as np
from flask import current_app


def _get_model_file():
    return current_app.config.get('MODEL_FILE',
           os.path.join(os.path.dirname(__file__), 'crime_model.pkl'))


# ── Feature Engineering ────────────────────────────────────────────────────────

def _build_features(location_stats: dict) -> tuple:
    """
    Convert raw crime stats into numeric feature vectors for sklearn.

    Features per location:
      0 – total_incidents
      1 – average_severity
      2 – unique_crime_types
      3 – incidents_last_30_days
      4 – incidents_last_90_days

    Labels:
      2 = High Risk   (top 25%)
      1 = Medium Risk (middle 50%)
      0 = Low Risk    (bottom 25%)
    """
    locations = list(location_stats.keys())
    X = []
    for loc in locations:
        s = location_stats[loc]
        X.append([
            s['total'],
            s['avg_severity'],
            s['unique_types'],
            s['last_30'],
            s['last_90']
        ])

    X = np.array(X, dtype=float)

    # Assign risk labels based on total incident count percentiles
    totals = X[:, 0]
    p75    = np.percentile(totals, 75)
    p25    = np.percentile(totals, 25)

    y = []
    for t in totals:
        if t >= p75:
            y.append(2)   # High
        elif t >= p25:
            y.append(1)   # Medium
        else:
            y.append(0)   # Low

    return X, np.array(y), locations


def _gather_location_stats():
    """Query DB and aggregate per-location crime statistics."""
    from models.database import CrimeData
    from sqlalchemy import func
    from models.database import db
    from datetime import datetime, timedelta

    now       = datetime.utcnow()
    last_30   = now - timedelta(days=30)
    last_90   = now - timedelta(days=90)

    all_crimes = CrimeData.query.all()

    if not all_crimes:
        return {}

    stats = {}
    for crime in all_crimes:
        loc = crime.location
        if loc not in stats:
            stats[loc] = {'total': 0, 'severity_sum': 0, 'types': set(),
                          'last_30': 0, 'last_90': 0}
        stats[loc]['total']        += 1
        stats[loc]['severity_sum'] += crime.severity
        stats[loc]['types'].add(crime.type)
        if crime.date >= last_30:
            stats[loc]['last_30'] += 1
        if crime.date >= last_90:
            stats[loc]['last_90'] += 1

    # Finalise aggregates
    for loc in stats:
        s = stats[loc]
        s['avg_severity']  = s['severity_sum'] / s['total']
        s['unique_types']  = len(s['types'])
        del s['types']
        del s['severity_sum']

    return stats


# ── Model Training ─────────────────────────────────────────────────────────────

def train_model():
    """Train (or retrain) the Random Forest classifier and save to disk."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler

        stats = _gather_location_stats()
        if len(stats) < 3:
            return None   # Not enough data to train

        X, y, locations = _build_features(stats)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_scaled, y)

        model_data = {'clf': clf, 'scaler': scaler, 'locations': locations}
        with open(_get_model_file(), 'wb') as f:
            pickle.dump(model_data, f)

        return model_data

    except ImportError:
        return None   # sklearn not installed


def _load_or_train():
    """Load saved model from disk, or train a fresh one."""
    model_file = _get_model_file()
    if os.path.exists(model_file):
        with open(model_file, 'rb') as f:
            return pickle.load(f)
    return train_model()


# ── Prediction API ─────────────────────────────────────────────────────────────

RISK_LABELS = {2: 'High', 1: 'Medium', 0: 'Low'}
RISK_COLORS = {2: '#ef4444', 1: '#f59e0b', 0: '#22c55e'}

def predict_risk_areas() -> list:
    """
    Return risk predictions for all locations in the database.
    Falls back to simple heuristic if sklearn is unavailable.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        return _heuristic_risk()

    stats = _gather_location_stats()
    if not stats:
        return []

    # Always retrain on latest data
    model_data = train_model()
    if model_data is None:
        return _heuristic_risk()

    clf    = model_data['clf']
    scaler = model_data['scaler']

    results = []
    for loc, s in stats.items():
        features = np.array([[s['total'], s['avg_severity'],
                               s['unique_types'], s['last_30'], s['last_90']]])
        features_scaled = scaler.transform(features)
        pred    = int(clf.predict(features_scaled)[0])
        proba   = clf.predict_proba(features_scaled)[0]
        conf    = round(float(max(proba)) * 100, 1)

        results.append({
            'location':    loc,
            'risk_level':  RISK_LABELS[pred],
            'risk_score':  pred,
            'confidence':  conf,
            'color':       RISK_COLORS[pred],
            'total_crimes': int(s['total']),
            'avg_severity': round(s['avg_severity'], 2)
        })

    # Sort: High → Medium → Low
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results


def _heuristic_risk() -> list:
    """Simple count-based fallback when sklearn is not available."""
    stats = _gather_location_stats()
    if not stats:
        return []

    totals    = [s['total'] for s in stats.values()]
    max_total = max(totals) if totals else 1
    results   = []

    for loc, s in stats.items():
        ratio = s['total'] / max_total
        if ratio >= 0.6:
            risk = 2
        elif ratio >= 0.3:
            risk = 1
        else:
            risk = 0

        results.append({
            'location':     loc,
            'risk_level':   RISK_LABELS[risk],
            'risk_score':   risk,
            'confidence':   round(ratio * 100, 1),
            'color':        RISK_COLORS[risk],
            'total_crimes': int(s['total']),
            'avg_severity': round(s['avg_severity'], 2)
        })

    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results


def get_hotspot_analysis() -> list:
    """
    Return top-10 hotspots with enriched details:
    most common crime type, risk level, incident count.
    """
    from models.database import CrimeData
    from collections import Counter

    crimes = CrimeData.query.all()
    if not crimes:
        return []

    hotspot_map = {}
    for c in crimes:
        if c.location not in hotspot_map:
            hotspot_map[c.location] = {'types': [], 'severities': [], 'count': 0}
        hotspot_map[c.location]['types'].append(c.type)
        hotspot_map[c.location]['severities'].append(c.severity)
        hotspot_map[c.location]['count'] += 1

    risk_map = {r['location']: r for r in predict_risk_areas()}

    hotspots = []
    for loc, data in hotspot_map.items():
        top_type = Counter(data['types']).most_common(1)[0][0]
        avg_sev  = sum(data['severities']) / len(data['severities'])
        risk     = risk_map.get(loc, {'risk_level': 'Unknown', 'color': '#6b7280'})

        hotspots.append({
            'location':       loc,
            'total_incidents': int(data['count']),
            'top_crime_type': top_type,
            'avg_severity':   round(avg_sev, 2),
            'risk_level':     risk['risk_level'],
            'color':          risk['color']
        })

    hotspots.sort(key=lambda x: x['total_incidents'], reverse=True)
    return hotspots[:10]


def _get_probability_model_file():
    return current_app.config.get('PROBABILITY_MODEL_FILE',
           os.path.join(os.path.dirname(__file__), 'crime_probability_model.pkl'))


def _build_probability_training_data(history_days: int = 90, target_days: int = 30):
    """Build hourly training samples for the logistic regression probability model."""
    from datetime import datetime, timedelta
    from models.database import CrimeData

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    history_start = now - timedelta(days=history_days)
    prediction_start = now - timedelta(days=target_days)

    crimes = CrimeData.query.filter(CrimeData.date >= history_start).order_by(CrimeData.date).all()
    if not crimes:
        return None, None

    locations = sorted({c.location for c in crimes})
    if not locations:
        return None, None

    location_events = {loc: [c for c in crimes if c.location == loc] for loc in locations}

    X = []
    y = []
    for location, loc_crimes in location_events.items():
        for hour_offset in range(target_days * 24):
            query_time = prediction_start + timedelta(hours=hour_offset)
            if query_time + timedelta(hours=1) > now:
                break

            window_30 = query_time - timedelta(days=30)
            window_7 = query_time - timedelta(days=7)

            past_30 = [c for c in loc_crimes if window_30 <= c.date < query_time]
            past_7 = [c for c in past_30 if c.date >= window_7]

            total_30 = len(past_30)
            total_7 = len(past_7)
            avg_severity = float(sum(c.severity for c in past_30) / total_30) if total_30 else 0.0
            unique_types = len({c.type for c in past_30})

            future_window_start = query_time
            future_window_end = query_time + timedelta(hours=1)
            label = int(any(future_window_start <= c.date < future_window_end for c in loc_crimes))

            X.append([total_30, total_7, avg_severity, unique_types, query_time.hour, query_time.weekday()])
            y.append(label)

    if not X or len(set(y)) < 2:
        return None, None

    return np.array(X, dtype=float), np.array(y, dtype=int)


def train_probability_model():
    """Train a logistic regression probability model and save it to disk."""
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.exceptions import ConvergenceWarning
        import warnings
        from datetime import datetime

        X, y = _build_probability_training_data()
        if X is None or y is None or len(y) < 20:
            return None

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=ConvergenceWarning)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            clf = LogisticRegression(random_state=42, solver='liblinear', max_iter=500)
            clf.fit(X_scaled, y)

        model_data = {'clf': clf, 'scaler': scaler}
        with open(_get_probability_model_file(), 'wb') as f:
            pickle.dump(model_data, f)

        return model_data
    except ImportError:
        return None
    except Exception:
        return None


def _load_or_train_probability_model():
    model_file = _get_probability_model_file()
    if os.path.exists(model_file):
        try:
            with open(model_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    return train_probability_model()


def _build_probability_features(location: str, query_time):
    from datetime import timedelta
    from models.database import CrimeData

    window_30 = query_time - timedelta(days=30)
    window_7 = query_time - timedelta(days=7)

    recent_crimes = CrimeData.query.filter(
        CrimeData.location == location,
        CrimeData.date >= window_30,
        CrimeData.date < query_time
    ).all()

    total_30 = len(recent_crimes)
    total_7 = sum(1 for c in recent_crimes if c.date >= window_7)
    avg_severity = float(sum(c.severity for c in recent_crimes) / total_30) if total_30 else 0.0
    unique_types = len({c.type for c in recent_crimes})

    return [total_30, total_7, avg_severity, unique_types, query_time.hour, query_time.weekday()]


def _heuristic_probability(location: str, query_time):
    from datetime import timedelta
    from models.database import CrimeData

    window_30 = query_time - timedelta(days=30)
    window_7 = query_time - timedelta(days=7)

    recent_crimes = CrimeData.query.filter(
        CrimeData.location == location,
        CrimeData.date >= window_30,
        CrimeData.date < query_time
    ).all()

    total_30 = len(recent_crimes)
    total_7 = sum(1 for c in recent_crimes if c.date >= window_7)
    score = min(0.99, 0.05 + total_30 * 0.02 + total_7 * 0.03)
    return score


def predict_crime_probability(location: str, query_time):
    """Return a crime probability prediction for a given location and datetime."""
    try:
        model_data = _load_or_train_probability_model()
        features = _build_probability_features(location, query_time)
        if model_data is None or features is None:
            probability = _heuristic_probability(location, query_time)
            predicted = probability >= 0.5
            return {
                'location': location,
                'datetime': query_time.strftime('%Y-%m-%d %H:%M'),
                'probability': round(probability * 100, 1),
                'predicted_crime': predicted,
                'features': {
                    'total_last_30_days': features[0] if features is not None else 0,
                    'total_last_7_days': features[1] if features is not None else 0,
                    'avg_severity': features[2] if features is not None else 0.0,
                    'unique_types': features[3] if features is not None else 0,
                    'hour': query_time.hour,
                    'weekday': query_time.weekday()
                }
            }

        clf = model_data['clf']
        scaler = model_data['scaler']
        X = np.array([features], dtype=float)
        X_scaled = scaler.transform(X)
        probability = float(clf.predict_proba(X_scaled)[0][1])
        predicted = bool(clf.predict(X_scaled)[0])

        return {
            'location': location,
            'datetime': query_time.strftime('%Y-%m-%d %H:%M'),
            'probability': round(probability * 100, 1),
            'predicted_crime': predicted,
            'features': {
                'total_last_30_days': features[0],
                'total_last_7_days': features[1],
                'avg_severity': features[2],
                'unique_types': features[3],
                'hour': query_time.hour,
                'weekday': query_time.weekday()
            }
        }
    except ImportError:
        probability = _heuristic_probability(location, query_time)
        return {
            'location': location,
            'datetime': query_time.strftime('%Y-%m-%d %H:%M'),
            'probability': round(probability * 100, 1),
            'predicted_crime': probability >= 0.5,
            'features': {
                'total_last_30_days': features[0] if features is not None else 0,
                'total_last_7_days': features[1] if features is not None else 0,
                'avg_severity': features[2] if features is not None else 0.0,
                'unique_types': features[3] if features is not None else 0,
                'hour': query_time.hour,
                'weekday': query_time.weekday()
            }
        }
    except Exception:
        return None
