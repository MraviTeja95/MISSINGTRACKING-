"""
REST API routes for Crime Data
  POST /api/crime/add       – Add a crime incident
  GET  /api/crime/list      – Fetch all incidents
  GET  /api/crime/stats     – Aggregated stats (location counts, type counts)
  GET  /api/crime/trends    – Monthly trend data
  POST /api/crime/reseed    – Reseed sample crime data
"""

from flask import Blueprint, request, jsonify, current_app
from models.database import db, CrimeData
from sqlalchemy import func
from datetime import datetime, timedelta

crime_bp = Blueprint('crime', __name__)


@crime_bp.route('/add', methods=['POST'])
def add_crime():
    """Add a new crime incident."""
    try:
        data     = request.get_json()
        location = data.get('location', '').strip()
        ctype    = data.get('type', '').strip()
        severity = int(data.get('severity', 1))
        lat      = data.get('lat')
        lng      = data.get('lng')
        date_str = data.get('date')

        if not location or not ctype:
            return jsonify({'success': False, 'error': 'Location and type are required'}), 400

        crime = CrimeData(
            location=location,
            type=ctype,
            severity=severity,
            lat=lat,
            lng=lng,
            date=datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        )
        db.session.add(crime)
        db.session.commit()
        return jsonify({'success': True, 'id': crime.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@crime_bp.route('/list', methods=['GET'])
def list_crimes():
    """Return all crime records."""
    crimes = CrimeData.query.order_by(CrimeData.date.desc()).all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in crimes], 'count': len(crimes)})


@crime_bp.route('/stats', methods=['GET'])
def crime_stats():
    """
    Returns aggregated stats used by the dashboard:
    - crimes_by_location : [{location, count}]
    - crimes_by_type     : [{type, count}]
    - severity_avg       : average severity across all incidents
    """
    try:
        # Crimes grouped by location
        by_location = (
            db.session.query(CrimeData.location, func.count(CrimeData.id).label('count'))
            .group_by(CrimeData.location)
            .order_by(func.count(CrimeData.id).desc())
            .limit(10)
            .all()
        )

        # Crimes grouped by type
        by_type = (
            db.session.query(CrimeData.type, func.count(CrimeData.id).label('count'))
            .group_by(CrimeData.type)
            .order_by(func.count(CrimeData.id).desc())
            .all()
        )

        avg_severity = db.session.query(func.avg(CrimeData.severity)).scalar() or 0

        return jsonify({
            'success': True,
            'crimes_by_location': [{'location': r[0], 'count': r[1]} for r in by_location],
            'crimes_by_type':     [{'type': r[0], 'count': r[1]} for r in by_type],
            'severity_avg':       round(float(avg_severity), 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@crime_bp.route('/trends', methods=['GET'])
def crime_trends():
    """
    Returns monthly crime counts for the last 12 months,
    plus monthly missing persons reports.
    """
    try:
        from models.database import MissingPerson

        months_data = []
        now = datetime.utcnow()

        for i in range(11, -1, -1):
            start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1, day=1)
            else:
                end = start.replace(month=start.month + 1, day=1)

            crime_count = CrimeData.query.filter(
                CrimeData.date >= start, CrimeData.date < end
            ).count()

            missing_count = MissingPerson.query.filter(
                MissingPerson.date_reported >= start,
                MissingPerson.date_reported < end
            ).count()

            months_data.append({
                'month':   start.strftime('%b %Y'),
                'crimes':  crime_count,
                'missing': missing_count
            })

        return jsonify({'success': True, 'data': months_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@crime_bp.route('/reseed', methods=['POST'])
def reseed_crimes():
    """
    Clear and reseed crime data with sample data for demo/testing.
    Useful when the map is empty.
    """
    try:
        from utils.seed_data import seed_crime_data
        
        # Clear existing crime data
        count_before = CrimeData.query.count()
        CrimeData.query.delete()
        db.session.commit()
        
        # Reseed with sample data
        seed_crime_data()
        
        count_after = CrimeData.query.count()
        current_app.logger.info(f"Reseeded crime data: removed {count_before}, added {count_after}")
        
        return jsonify({
            'success': True,
            'message': f'Crime data reseeded successfully',
            'removed': count_before,
            'added': count_after
        }), 200
    except Exception as e:
        current_app.logger.error(f"Reseed error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
