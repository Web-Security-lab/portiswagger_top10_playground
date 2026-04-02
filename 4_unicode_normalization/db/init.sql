USE polylot_db;

CREATE TABLE IF NOT EXISTS users (
    id            INT           NOT NULL AUTO_INCREMENT,
    email         VARCHAR(255)  NOT NULL,
    display_name  VARCHAR(100)  NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS notes (
    id         INT           NOT NULL AUTO_INCREMENT,
    user_id    INT           NOT NULL,
    title      VARCHAR(255)  NOT NULL,
    content    TEXT          NOT NULL,
    language   VARCHAR(10)   NOT NULL DEFAULT 'en',
    is_public  TINYINT(1)    NOT NULL DEFAULT 0,
    created_at TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_notes_public (is_public, created_at),
    KEY idx_notes_user   (user_id),
    CONSTRAINT fk_notes_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS admin_sessions (
    id        INT          NOT NULL AUTO_INCREMENT,
    api_token VARCHAR(64)  NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;

INSERT INTO admin_sessions (api_token)
VALUES ('4dm1n-4p1-t0k3n-s3cr3t-2025-p0ly10t');