import sqlite3

DB_NAME = "tasks.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    with connect() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

def add_user(username, password, role):
    with connect() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()

def get_user(username, password):
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        return c.fetchone()

def add_task(task, user_id):
    with connect() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (task, user_id) VALUES (?, ?)", (task, user_id))
        conn.commit()

def get_tasks_for_assigner():
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT task, user_id FROM tasks")
        return c.fetchall()

def get_tasks_for_user(user_id):
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT task FROM tasks WHERE user_id = ?", (user_id,))
        return c.fetchall()
