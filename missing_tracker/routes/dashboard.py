"""
Dashboard Route
  GET /api/dashboard/summary – Combined stats for the main dashboard
  GET /api/dashboard/crime-density – Geographic crime data for map
"""

from flask import Blueprint, jsonify, current_app
from models.database import db, MissingPerson, CrimeData
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/summary', methods=['GET'])
def summary():
    """
    Returns a comprehensive summary for the dashboard:
    - total_missing, total_found, total_crimes
    - recent_missing (last 5)
    - crimes_by_location (top 8)
    - crimes_by_type
    - monthly_trends (12 months)
    - risk_predictions (from ML)
    """
    try:
        # Counts
        total_missing = int(MissingPerson.query.filter_by(status='missing').count())
        total_found   = int(MissingPerson.query.filter_by(status='found').count())
        total_crimes  = int(CrimeData.query.count())

        # Recent missing persons
        recent = MissingPerson.query.filter_by(status='missing')\
                    .order_by(MissingPerson.date_reported.desc()).limit(5).all()

        # Crime breakdown
        by_location_raw = (
            db.session.query(CrimeData.location, func.count(CrimeData.id).label('count'))
            .group_by(CrimeData.location)
            .order_by(func.count(CrimeData.id).desc())
            .limit(8).all()
        )

        by_type_raw = (
            db.session.query(CrimeData.type, func.count(CrimeData.id).label('count'))
            .group_by(CrimeData.type)
            .order_by(func.count(CrimeData.id).desc())
            .all()
        )
        
        # Convert int64 to int for JSON serialization
        by_location = [{'location': loc, 'count': int(cnt)} for loc, cnt in by_location_raw]
        by_type = [{'type': typ, 'count': int(cnt)} for typ, cnt in by_type_raw]

        # Monthly trends (12 months)
        months_data = []
        now = datetime.utcnow()
        for i in range(11, -1, -1):
            start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1, day=1)
            else:
                end = start.replace(month=start.month + 1, day=1)

            months_data.append({
                'month':   start.strftime('%b %Y'),
                'crimes':  int(CrimeData.query.filter(CrimeData.date >= start, CrimeData.date < end).count()),
                'missing': int(MissingPerson.query.filter(
                                MissingPerson.date_reported >= start,
                                MissingPerson.date_reported < end).count())
            })

        # Risk predictions + hotspots
        try:
            from utils.ml_utils import predict_risk_areas, get_hotspot_analysis
            risk_data = predict_risk_areas()
            hotspots = get_hotspot_analysis()
        except Exception:
            risk_data = []
            hotspots = []

        high_risk = sum(1 for r in risk_data if r.get('risk_score') == 2)

        return jsonify({
            'success': True,
            'stats': {
                'total_missing': total_missing,
                'total_found':   total_found,
                'total_crimes':  total_crimes,
                'high_risk':     high_risk,
            },
            'recent_missing':    [p.to_dict() for p in recent],
            'crimes_by_location': by_location,
            'crimes_by_type':     by_type,
            'monthly_trends':     months_data,
            'risk_predictions':   risk_data,
            'hotspots':           hotspots
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/crime-density', methods=['GET'])
def crime_density():
    """Return aggregated crime incident locations for map density visualization."""
    try:
        LOCATION_COORDINATES = {
            'MG Road': (12.9762, 77.5999),
            'Brigade Road': (12.9718, 77.6101),
            'Koramangala': (12.9352, 77.6245),
            'Indiranagar': (12.9719, 77.6412),
            'Whitefield': (12.9694, 77.7499),
            'Electronic City': (12.8446, 77.6770),
            'Jayanagar': (12.9250, 77.5938),
            'Marathahalli': (12.9676, 77.7153),
            'HSR Layout': (12.9141, 77.6476),
            'BTM Layout': (12.9250, 77.6002),
            'Rajajinagar': (12.9950, 77.5498),
            'Malleswaram': (13.0103, 77.5647),
            'Yeshwanthpur': (13.0190, 77.5535),
            'Hebbal': (13.0365, 77.5970),
            'Yelahanka': (13.0845, 77.5937),
        }

        # Get crime density by location
        density = (
            db.session.query(
                CrimeData.location,
                func.count(CrimeData.id).label('count'),
                func.avg(CrimeData.lat).label('avg_lat'),
                func.avg(CrimeData.lng).label('avg_lng')
            )
            .group_by(CrimeData.location)
            .order_by(func.count(CrimeData.id).desc())
            .all()
        )

        payload = []
        for loc, cnt, lat, lng in density:
            # Try to use stored lat/lng
            if lat is None or lng is None:
                # Fall back to hardcoded coordinates
                fallback = LOCATION_COORDINATES.get(loc)
                if fallback is not None:
                    lat, lng = fallback
            
            # Skip entries with no valid coordinates
            if lat is None or lng is None:
                current_app.logger.warning(f"Skipping location '{loc}': no coordinates available")
                continue
            
            # Validate coordinates are proper numbers
            try:
                lat = float(lat)
                lng = float(lng)
            except (ValueError, TypeError):
                current_app.logger.warning(f"Skipping location '{loc}': invalid coordinate values")
                continue
            
            payload.append({
                'location': loc,
                'count': int(cnt),
                'avg_lat': lat,
                'avg_lng': lng
            })

        current_app.logger.info(f"Crime density: {len(payload)} locations with valid coordinates")
        
        if not payload:
            current_app.logger.warning("No crime data with valid coordinates found")
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No geographic crime data available'
            })

        return jsonify({'success': True, 'data': payload})
    except Exception as e:
        current_app.logger.error(f"Crime density error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
