"""
Authentication routes using Flask-Login.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse, urljoin

from models.database import db, User

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target: str) -> bool:
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc


def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': 'Forbidden: insufficient privileges'}), 403
                flash('You do not have permission to access that page.', 'danger')
                return redirect(url_for('ui.home'))
            return view(*args, **kwargs)
        return wrapped_view
    return decorator


def _is_ajax_request():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('ajax') == 'true'


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ui.home'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            redirect_target = next_page if next_page and is_safe_url(next_page) else url_for('ui.home')
            if _is_ajax_request():
                return jsonify({'success': True, 'redirect': redirect_target})
            flash('Logged in successfully.', 'success')
            return redirect(redirect_target)

        if _is_ajax_request():
            return jsonify({'success': False, 'error': 'Invalid username/email or password.'})
        flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', page_type='regular')


@auth_bp.route('/police-login', methods=['GET', 'POST'])
def police_login():
    if current_user.is_authenticated:
        return redirect(url_for('ui.home'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            if user.role not in ('Admin', 'Police'):
                if _is_ajax_request():
                    return jsonify({'success': False, 'error': 'Access denied. This portal is for Police and Admin personnel only.'})
                flash('Access denied. This portal is for Police and Admin personnel only.', 'danger')
                return render_template('login.html', page_type='police')
            login_user(user)
            next_page = request.args.get('next')
            redirect_target = next_page if next_page and is_safe_url(next_page) else url_for('ui.home')
            if _is_ajax_request():
                return jsonify({'success': True, 'redirect': redirect_target})
            flash('Logged in successfully.', 'success')
            return redirect(redirect_target)

        if _is_ajax_request():
            return jsonify({'success': False, 'error': 'Invalid username/email or password.'})
        flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', page_type='police')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('ui.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'Public').title()

        if not username or not email or not password or not confirm_password:
            if _is_ajax_request():
                return jsonify({'success': False, 'error': 'Please fill in all fields.'})
            flash('Please fill in all fields.', 'danger')
            return render_template('signup.html', username=username, email=email, role=role)

        if password != confirm_password:
            if _is_ajax_request():
                return jsonify({'success': False, 'error': 'Passwords do not match.'})
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html', username=username, email=email, role=role)

        if User.query.filter_by(username=username).first():
            if _is_ajax_request():
                return jsonify({'success': False, 'error': 'That username is already taken.'})
            flash('That username is already taken.', 'danger')
            return render_template('signup.html', username=username, email=email, role=role)

        if User.query.filter_by(email=email).first():
            if _is_ajax_request():
                return jsonify({'success': False, 'error': 'That email is already registered.'})
            flash('That email is already registered.', 'danger')
            return render_template('signup.html', username=username, email=email, role=role)

        if role not in ('Admin', 'Police', 'Public'):
            role = 'Public'

        user = User(username=username, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        login_user(user)

        if _is_ajax_request():
            return jsonify({'success': True, 'redirect': url_for('ui.home')})
        flash('Account created successfully. You are now logged in.', 'success')
        return redirect(url_for('ui.home'))

    return render_template('signup.html', page_type='regular')


@auth_bp.route('/police-signup')
def police_signup():
    if current_user.is_authenticated:
        return redirect(url_for('ui.home'))
    return render_template('signup.html', page_type='police')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('ui.home'))
