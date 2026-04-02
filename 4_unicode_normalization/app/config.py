import os


class Config:
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'polylot-notes-dev-secret-2025')

    DB_HOST: str = os.environ.get('DB_HOST', 'localhost')
    DB_PORT: int = int(os.environ.get('DB_PORT', '3306'))
    DB_USER: str = os.environ.get('DB_USER', 'polylot')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD', 'p0ly10t_db_s3cr3t_2025')
    DB_NAME: str = os.environ.get('DB_NAME', 'polylot_db')

    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour
