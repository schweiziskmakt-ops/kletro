import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_dir, 'my_db.db')

def create_connection():
    try:
        print("USING DATABASE:", DB_PATH)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")

