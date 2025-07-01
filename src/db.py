import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'geartrack.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            serial TEXT UNIQUE,
            date_in_service TEXT,
            condition TEXT,
            notes TEXT,
            image_path TEXT
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER,
            user_id INTEGER,
            action TEXT,
            timestamp TEXT,
            note TEXT
        );
        ''')
