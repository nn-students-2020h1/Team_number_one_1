import sqlite3

__connection = None

def get_connect():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('base.db')
    return __connection

def init_db(force: bool = False):
    conn = get_connect()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS user_message')
        print('!!!DROP!!!')
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_message (
            id         INTEGER PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            text       TEXT NOT NULL
        )
    """)
    conn.commit()

def add_message(user_id: int , text: str):
    conn = get_connect()
    c = conn.cursor()
    c.execute('INSERT INTO user_message (user_id,text) VALUES (?, ?)', (user_id,text))
    conn.commit()

if __name__ == '__main__':
    init_db()
    print('***')
    add_message(user_id=123,text='keks')