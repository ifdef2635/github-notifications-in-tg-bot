import sqlite3


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Таблица для подписок
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions 
                 (chat_id INTEGER PRIMARY KEY)''')
    # Таблица для соответствия GitHub-логин и chat_id
    c.execute('''CREATE TABLE IF NOT EXISTS user_mapping 
                 (chat_id INTEGER, github_login TEXT, 
                  PRIMARY KEY (chat_id, github_login))''')
    conn.commit()
    conn.close()


def add_user_mapping(chat_id, github_login):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO user_mapping (chat_id, github_login) VALUES (?, ?)',
              (chat_id, github_login))
    conn.commit()
    conn.close()


def get_chat_id_by_github_login(github_login):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM user_mapping WHERE github_login = ?', (github_login,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def add(chat_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO subscriptions VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()


def remove(chat_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM subscriptions WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM subscriptions')
    subscriptions = [row[0] for row in c.fetchall()]
    conn.close()
    return subscriptions
