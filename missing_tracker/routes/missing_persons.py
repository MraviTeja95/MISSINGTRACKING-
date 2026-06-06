"""
REST API routes for Missing Person records
  POST /api/missing/add          – Report a new missing person
  GET  /api/missing/list         – Fetch all records
  GET  /api/missing/<id>         – Fetch single record
  PUT  /api/missing/<id>/status  – Update found/missing status
  DELETE /api/missing/<id>       – Delete a record
"""

import os
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models.database import db, MissingPerson
from utils.helpers import allowed_file

missing_bp = Blueprint('missing', __name__)


def _can_view_sensitive_missing_person_data() -> bool:
    return current_user.is_authenticated and current_user.role in ('Admin', 'Police')


@missing_bp.route('/add', methods=['POST'])
def add_missing_person():
    """Add a new missing person report with optional photo upload."""
    try:
        name      = request.form.get('name', '').strip()
        age       = request.form.get('age', 0)
        last_seen = request.form.get('last_seen', '').strip()
        description = request.form.get('description', '').strip()
        contact   = request.form.get('contact', '').strip()

        if not name or not last_seen:
            return jsonify({'success': False, 'error': 'Name and last_seen are required'}), 400

        photo_filename = None

        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                filename = secure_filename(file.filename)
                # Make filename unique with timestamp
                import time
                base, ext = os.path.splitext(filename)
                photo_filename = f"{base}_{int(time.time())}{ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo_filename)
                file.save(upload_path)
                # Note: Face encoding will be done after person is created with proper ID

        person = MissingPerson(
            name=name,
            age=int(age),
            photo=photo_filename,
            last_seen=last_seen,
            description=description,
            contact=contact
        )
        db.session.add(person)
        db.session.commit()

        # Now store face encoding with the real DB id
        if photo_filename:
            try:
                from utils.face_utils import update_face_encodings
                update_face_encodings(
                    os.path.join(current_app.config['UPLOAD_FOLDER'], photo_filename),
                    int_id=person.id
                )
            except Exception as fe:
                current_app.logger.warning(f"Face encoding store failed: {fe}")

        return jsonify({'success': True, 'message': 'Missing person reported successfully', 'id': person.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@missing_bp.route('/list', methods=['GET'])
def list_missing_persons():
    """Return all missing person records, newest first."""
    try:
        status = request.args.get('status')          # optional filter: missing | found
        query  = MissingPerson.query.order_by(MissingPerson.date_reported.desc())
        if status:
            query = query.filter_by(status=status)
        persons = query.all()
        include_sensitive = _can_view_sensitive_missing_person_data()
        return jsonify({
            'success': True,
            'data': [p.to_dict(include_sensitive=include_sensitive) for p in persons],
            'count': len(persons)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@missing_bp.route('/<int:person_id>', methods=['GET'])
def get_missing_person(person_id):
    """Return a single missing person record."""
    person = MissingPerson.query.get_or_404(person_id)
    return jsonify({
        'success': True,
        'data': person.to_dict(include_sensitive=_can_view_sensitive_missing_person_data())
    })

@missing_bp.route('/<int:person_id>/status', methods=['PUT'])
@login_required
def update_status(person_id):
    """Mark a person as found or missing."""
    if current_user.role not in ('Admin', 'Police'):
        return jsonify({'success': False, 'error': 'Forbidden: insufficient privileges'}), 403

    person = MissingPerson.query.get_or_404(person_id)
    data = request.get_json()
    new_status = data.get('status', 'missing')
    if new_status not in ('missing', 'found'):
        return jsonify({'success': False, 'error': 'Status must be missing or found'}), 400
    person.status = new_status
    db.session.commit()
    return jsonify({'success': True, 'message': f'Status updated to {new_status}'})


@missing_bp.route('/<int:person_id>', methods=['DELETE'])
@login_required
def delete_missing_person(person_id):
    """Delete a missing person record."""
    if current_user.role not in ('Admin', 'Police'):
        return jsonify({'success': False, 'error': 'Forbidden: insufficient privileges'}), 403

    person = MissingPerson.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Record deleted'})
