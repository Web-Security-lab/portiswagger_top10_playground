import re
import unicodedata

import pymysql.err
from flask import Blueprint, request, jsonify, session
from ..db import get_db

api_bp = Blueprint('api', __name__)


def _login_required_api(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

_WAF_SQLI = re.compile(
    r'\b(?:union|select|insert|update|delete|drop|'
    r'create|alter|exec|sleep|benchmark|load_file|'
    r'outfile|information_schema|schema|database|'
    r'version|user|having|group\s+by)\b',
    re.IGNORECASE
)

@api_bp.route('/notes/search')
@_login_required_api
def search_notes():
    q_raw = request.args.get('q', '')[:200]

    if _WAF_SQLI.search(q_raw):
        return jsonify({'error': 'WAF: suspicious pattern detected in query'}), 403

    q = unicodedata.normalize('NFKC', q_raw)

    db = get_db()
    with db.cursor() as cur:
        sql = (
            "SELECT n.id, n.title, LEFT(n.content, 300) AS preview, u.display_name "
            "FROM   notes n "
            "JOIN   users u ON n.user_id = u.id "
            f"WHERE  n.is_public = 1 AND n.title LIKE '%{q}%' "
            "ORDER BY n.created_at DESC "
            "LIMIT  10"
        )
        cur.execute(sql)
        rows = cur.fetchall()

    return jsonify(rows)

@api_bp.route('/notes', methods=['POST'])
@_login_required_api
def create_note():
    data     = request.get_json(silent=True) or {}
    title    = str(data.get('title',    '')).strip()
    content  = str(data.get('content',  '')).strip()
    language = str(data.get('language', 'en')).strip()[:10]
    is_public = bool(data.get('is_public', False))

    if not title or not content:
        return jsonify({'error': "'title' and 'content' are required"}), 400

    if len(title) > 255:
        return jsonify({'error': "'title' must be ≤ 255 characters"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO notes (user_id, title, content, language, is_public) "
            "VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], title, content, language, int(is_public))
        )
        note_id = cur.lastrowid

    return jsonify({'id': note_id, 'message': 'Note created successfully'}), 201

@api_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@_login_required_api
def delete_note(note_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM notes WHERE id = %s AND user_id = %s",
            (note_id, session['user_id'])
        )
        affected = cur.rowcount

    if affected == 0:
        return jsonify({'error': 'Note not found or permission denied'}), 404

    return jsonify({'message': 'Note deleted'})


@api_bp.route('/notes/<int:note_id>', methods=['PATCH'])
@_login_required_api
def update_note(note_id):
    data      = request.get_json(silent=True) or {}
    title     = data.get('title')
    content   = data.get('content')
    is_public = data.get('is_public')

    updates = {}
    if title     is not None: updates['title']     = str(title)[:255]
    if content   is not None: updates['content']   = str(content)
    if is_public is not None: updates['is_public'] = int(bool(is_public))

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    set_clause = ', '.join(f"{k} = %s" for k in updates)
    values     = list(updates.values()) + [note_id, session['user_id']]

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            f"UPDATE notes SET {set_clause} WHERE id = %s AND user_id = %s",
            values
        )
        affected = cur.rowcount

    if affected == 0:
        return jsonify({'error': 'Note not found or permission denied'}), 404

    return jsonify({'message': 'Note updated'})

@api_bp.route('/whoami')
@_login_required_api
def whoami():
    return jsonify({
        'user_id':      session.get('user_id'),
        'display_name': session.get('display_name'),
    })
