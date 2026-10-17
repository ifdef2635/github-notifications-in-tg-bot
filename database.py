import sqlite3
from contextlib import closing

DB_PATH = 'users.db'


def _connect():
    return closing(sqlite3.connect(DB_PATH))


def init_db():
    with _connect() as conn:
        # Таблица для подписок
        conn.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                        (chat_id INTEGER PRIMARY KEY)''')
        # Таблица для соответствия GitHub-логин и chat_id
        conn.execute('''CREATE TABLE IF NOT EXISTS user_mapping
                        (chat_id INTEGER, github_login TEXT,
                         PRIMARY KEY (chat_id, github_login))''')
        conn.commit()


def add_user_mapping(chat_id, github_login):
    """Привязывает логин к чату. У чата один логин, у логина один чат —
    прежние привязки заменяются (логины GitHub не зависят от регистра)."""
    with _connect() as conn:
        conn.execute('DELETE FROM user_mapping WHERE chat_id = ? '
                     'OR github_login = ? COLLATE NOCASE', (chat_id, github_login))
        conn.execute('INSERT INTO user_mapping (chat_id, github_login) VALUES (?, ?)',
                     (chat_id, github_login))
        conn.commit()


def get_chat_id_by_github_login(github_login):
    with _connect() as conn:
        row = conn.execute(
            'SELECT chat_id FROM user_mapping WHERE github_login = ? COLLATE NOCASE',
            (github_login,)).fetchone()
    return row[0] if row else None


def add(chat_id):
    with _connect() as conn:
        conn.execute('INSERT OR IGNORE INTO subscriptions VALUES (?)', (chat_id,))
        conn.commit()


def remove(chat_id):
    """Полная отписка: убирает и подписку, и привязку GitHub-логина."""
    with _connect() as conn:
        conn.execute('DELETE FROM subscriptions WHERE chat_id = ?', (chat_id,))
        conn.execute('DELETE FROM user_mapping WHERE chat_id = ?', (chat_id,))
        conn.commit()


def get_all():
    with _connect() as conn:
        return [row[0] for row in conn.execute('SELECT chat_id FROM subscriptions')]
