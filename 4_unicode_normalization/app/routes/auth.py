import logging
import unicodedata
from flask import (Blueprint, request, session, redirect,
                   url_for, render_template, flash, jsonify)
import pymysql.err
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import get_db
from ..utils.normalizer import safe_normalize

log = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email        = request.form.get('email', '').strip()
        display_name = request.form.get('display_name', '').strip()
        password     = request.form.get('password', '')

        if not email or not display_name or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        if len(email) > 254:
            flash('Email address is too long.', 'error')
            return render_template('register.html')

        normalized_name = safe_normalize(display_name)

        db = get_db()
        try:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )
                if cur.fetchone():
                    flash('This email is already registered.', 'error')
                    return render_template('register.html')

                pw_hash = generate_password_hash(password)
                cur.execute(
                    "INSERT INTO users (email, display_name, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (email, normalized_name, pw_hash)
                )

        except pymysql.err.IntegrityError:
            flash('This email is already registered.', 'error')
            return render_template('register.html')

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, display_name, password_hash "
                "FROM   users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id']      = user['id']
            session['display_name'] = user['display_name']
            session.permanent       = True
            return redirect(url_for('main.dashboard'))

        flash('Invalid email or password.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    if request.is_json:
        data  = request.get_json(silent=True) or {}
        email = data.get('email', '').strip()
    else:
        email = request.form.get('email', '').strip()

    if not email:
        return jsonify({'error': 'email is required'}), 400

    log.info("Password reset requested for: %s", email)

    return jsonify({
        'message': 'If this email exists in our system, '
                   'you will receive a reset link shortly.'
    })