import sqlite3


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions 
                 (chat_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()


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
