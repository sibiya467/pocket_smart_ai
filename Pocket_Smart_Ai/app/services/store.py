import json
import sqlite3

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "pocketsmart.db"


def _connection():

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    with _connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
            """
        )


def create_user(
    name,
    email,
    password_hash
):

    from datetime import (
        datetime,
        timezone
    )

    with _connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email.lower(),
                password_hash,
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        )

        return cursor.lastrowid


def get_user_by_email(email):

    with _connection() as connection:

        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (email.lower(),)
        ).fetchone()


def save_history(
    user_id,
    planner,
    request_data,
    response_data
):

    from datetime import (
        datetime,
        timezone
    )

    with _connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO history
            (
                user_id,
                planner,
                request_json,
                response_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                planner,
                json.dumps(request_data),
                json.dumps(response_data),
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        )

        return cursor.lastrowid


def list_history(user_id):

    with _connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                planner,
                request_json,
                response_json,
                created_at
            FROM history
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


def get_history(
    user_id,
    history_id
):

    with _connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM history
            WHERE id=?
            AND user_id=?
            """,
            (
                history_id,
                user_id
            )
        ).fetchone()

        return (
            dict(row)
            if row
            else None
        )