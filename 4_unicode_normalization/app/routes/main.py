from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, abort
from ..db import get_db

main_bp = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@main_bp.route('/')
def index():
    """Homepage — shows recent public notes."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT n.id, n.title, LEFT(n.content, 220) AS preview, "
            "       u.display_name, n.language, n.created_at "
            "FROM   notes n "
            "JOIN   users u ON n.user_id = u.id "
            "WHERE  n.is_public = 1 "
            "ORDER BY n.created_at DESC "
            "LIMIT  6"
        )
        recent_notes = cur.fetchall()
    return render_template('index.html', notes=recent_notes)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Authenticated user's note dashboard."""
    user_id = session['user_id']
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, title, LEFT(content, 220) AS preview, "
            "       is_public, language, created_at "
            "FROM   notes "
            "WHERE  user_id = %s "
            "ORDER BY created_at DESC",
            (user_id,)
        )
        my_notes = cur.fetchall()
    return render_template('dashboard.html', notes=my_notes)

@main_bp.route('/notes/<int:note_id>')
def view_note(note_id):
    """View a single note (public or owned by current user)."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT n.id, n.title, n.content, n.language, n.is_public, "
            "       u.display_name, n.created_at "
            "FROM   notes n "
            "JOIN   users u ON n.user_id = u.id "
            "WHERE  n.id = %s "
            "  AND (n.is_public = 1 OR n.user_id = %s)",
            (note_id, session.get('user_id', -1))
        )
        note = cur.fetchone()

    if not note:
        abort(404)

    return render_template('note.html', note=note)