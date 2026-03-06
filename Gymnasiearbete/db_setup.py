import sqlite3
from werkzeug.security import generate_password_hash
from my_server.db_handler import create_connection


def init_db():
    conn = create_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        groups TEXT,
        friends TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        titel TEXT,
        content TEXT NOT NULL,
        content2 TEXT,
        grades TEXT,
        time TEXT,
        image_filename TEXT ,
        FOREIGN KEY (author_id) REFERENCES users(id)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        titel TEXT NOT NULL,
        content TEXT NOT NULL,
        privacy TEXT,
        image_filename TEXT,
        is_private INTEGER DEFAULT 0,
        FOREIGN KEY (author_id) REFERENCES users(id)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS friendships (
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    status TEXT NOT NULL,                
    requested_by INTEGER NOT NULL,        
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id1, user_id2),
    CHECK (user_id1 < user_id2),
    CHECK (requested_by = user_id1 OR requested_by = user_id2),
    FOREIGN KEY (user_id1) REFERENCES users(id),
    FOREIGN KEY (user_id2) REFERENCES users(id),
    FOREIGN KEY (requested_by) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
        

if __name__ == "__main__":
    init_db()
    print("DB initialized")