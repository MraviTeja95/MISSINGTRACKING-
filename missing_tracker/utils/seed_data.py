"""
Seed sample crime data into the database for demonstration.
Only seeds if the crime_data table is empty.
"""

from datetime import datetime, timedelta
import random


SAMPLE_CRIMES = [
    # (location, type, severity)
    ('MG Road',           'Robbery',          4),
    ('Brigade Road',      'Theft',            2),
    ('Koramangala',       'Assault',          3),
    ('Indiranagar',       'Vandalism',        2),
    ('Whitefield',        'Vehicle Theft',    3),
    ('Electronic City',   'Robbery',          4),
    ('Jayanagar',         'Theft',            2),
    ('Marathahalli',      'Assault',          3),
    ('HSR Layout',        'Vandalism',        1),
    ('BTM Layout',        'Drug Offense',     4),
    ('Rajajinagar',       'Robbery',          3),
    ('Malleswaram',       'Theft',            2),
    ('Yeshwanthpur',      'Vehicle Theft',    3),
    ('Hebbal',            'Assault',          2),
    ('Yelahanka',         'Vandalism',        1),
    ('MG Road',           'Assault',          3),
    ('Koramangala',       'Robbery',          5),
    ('Brigade Road',      'Drug Offense',     3),
    ('Whitefield',        'Theft',            2),
    ('Electronic City',   'Vehicle Theft',    4),
    ('Indiranagar',       'Robbery',          4),
    ('HSR Layout',        'Assault',          3),
    ('BTM Layout',        'Theft',            2),
    ('MG Road',           'Vehicle Theft',    3),
    ('Koramangala',       'Drug Offense',     4),
    ('Marathahalli',      'Robbery',          5),
    ('Jayanagar',         'Assault',          2),
    ('Brigade Road',      'Vandalism',        1),
    ('Rajajinagar',       'Drug Offense',     3),
    ('Whitefield',        'Robbery',          4),
]


SAMPLE_MISSING = [
    # (name, age, last_seen, description, contact)
    ('Priya Sharma', 28, 'Koramangala 4th Block', 'Wearing blue kurti and jeans, last seen near Forum Mall', '9876543210'),
    ('Rahul Kumar', 35, 'MG Road', 'Tall man with black hair, wearing white shirt and black pants', '9123456789'),
    ('Anjali Patel', 22, 'Indiranagar', 'Student, wearing red backpack, last seen near 100ft Road', '9988776655'),
    ('Vikram Singh', 45, 'Whitefield', 'Businessman, wearing suit, last seen near ITPL', '9876543211'),
    ('Meera Joshi', 31, 'HSR Layout', 'Teacher, wearing green saree, last seen near HSR BDA Complex', '9123456788'),
    ('Arjun Reddy', 26, 'Electronic City', 'Software engineer, wearing casual clothes, last seen near Infosys campus', '9988776654'),
    ('Kavita Nair', 29, 'BTM Layout', 'Doctor, wearing white coat, last seen near Apollo Hospital', '9876543212'),
    ('Suresh Babu', 52, 'Jayanagar', 'Retired person, wearing traditional clothes, last seen near Jayanagar 4th Block', '9123456787'),
]

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


def seed_crime_data():
    """Add sample crime records if table is empty."""
    from models.database import db, CrimeData

    if CrimeData.query.count() > 0:
        return   # Already seeded

    now = datetime.utcnow()
    crimes = []

    for i, (location, ctype, severity) in enumerate(SAMPLE_CRIMES):
        # Spread crimes over the last 12 months
        days_ago = random.randint(1, 365)
        lat, lng = LOCATION_COORDINATES.get(location, (None, None))
        crimes.append(CrimeData(
            location=location,
            type=ctype,
            severity=severity,
            date=now - timedelta(days=days_ago),
            lat=lat,
            lng=lng
        ))

    db.session.bulk_save_objects(crimes)
    db.session.commit()


def seed_missing_persons():
    """Add sample missing persons records if table is empty."""
    from models.database import db, MissingPerson

    if MissingPerson.query.count() > 0:
        return   # Already seeded

    now = datetime.utcnow()
    missing = []

    for i, (name, age, last_seen, description, contact) in enumerate(SAMPLE_MISSING):
        # Spread reports over the last 6 months
        days_ago = random.randint(1, 180)
        missing.append(MissingPerson(
            name=name,
            age=age,
            last_seen=last_seen,
            description=description,
            contact=contact,
            date_reported=now - timedelta(days=days_ago)
        ))

    db.session.bulk_save_objects(missing)
    db.session.commit()
