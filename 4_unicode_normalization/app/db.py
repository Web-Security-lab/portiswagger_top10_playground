import pymysql
import pymysql.cursors
from flask import current_app, g


def get_db() -> pymysql.Connection:
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return g.db

def close_db(e=None) -> None:
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass
