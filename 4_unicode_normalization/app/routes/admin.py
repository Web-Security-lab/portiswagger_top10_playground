import re
import unicodedata

from flask import Blueprint, request, jsonify, render_template_string
from ..db import get_db

admin_bp = Blueprint('admin', __name__)


def _verify_admin_token(token: str) -> bool:
    if not token or len(token) > 128:
        return False
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id FROM admin_sessions WHERE api_token = %s",
            (token,)
        )
        return cur.fetchone() is not None

_TEMPLATE_INJECTION_FILTER = re.compile(r"""[{}<>\[\]|'"\\`]""")

@admin_bp.route('/render')
def admin_render():
    token = request.headers.get('X-Admin-Token', '')
    if not _verify_admin_token(token):
        return jsonify({
            'error': 'Unauthorized: valid X-Admin-Token header is required'
        }), 403

    content = request.args.get('content', '')[:500]

    lang_raw = request.args.get('lang', 'en')[:10]
    lang     = lang_raw if re.match(r'^[A-Za-z0-9\-]{1,10}$', lang_raw) else 'und'

    if _TEMPLATE_INJECTION_FILTER.search(content):
        return jsonify({
            'error': "Forbidden: content contains disallowed characters "
                     "({ } < > [ ] | ' \" \\ `)"
        }), 400

    normalized_content = unicodedata.normalize('NFKC', content)

    template = f"<span lang='{lang}' class='translation'>{normalized_content}</span>"
    result   = render_template_string(template)

    return jsonify({'output': result, 'lang': lang})

@admin_bp.route('/status')
def admin_status():
    token = request.headers.get('X-Admin-Token', '')
    if not _verify_admin_token(token):
        return jsonify({'error': 'Unauthorized'}), 403

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM notes WHERE is_public = 1")
        public_count = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM users")
        user_count = cur.fetchone()['total']

    return jsonify({
        'status':        'ok',
        'public_notes':  public_count,
        'total_users':   user_count,
    })