import hashlib
from src.db import get_db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if not user:
        return None
    return user if hash_password(password) == user['password'] else None

def create_user(username, password, is_admin=False):
    db = get_db()
    db.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
               (username, hash_password(password), int(is_admin)))
    db.commit()
