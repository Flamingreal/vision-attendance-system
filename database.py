import sqlite3
from datetime import datetime
from typing import Optional

DATABASE_PATH = "attendance_system.db"

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                embedding BLOB NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        self.conn.commit()

        # Create default users if not present
        # if not self.get_all_users():
        #     # Default test accounts, useful for future login features
        #     self.add_user("alice", "1234", "Student")
        #     self.add_user("bob", "5678", "Teacher")
        #     self.add_user("admin", "admin", "Admin")
        #     self.add_user("dev", "devmode", "Developer")

    def add_new_face(self, name: str, embedding: bytes) -> bool:
        if self.face_exists(name):
            return False
        self.cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, embedding))
        self.conn.commit()
        return True

    def delete_face(self, name: str) -> bool:
        self.cursor.execute("DELETE FROM faces WHERE name = ?", (name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_face(self, name: str, new_embedding: bytes) -> bool:
        self.cursor.execute("UPDATE faces SET embedding = ? WHERE name = ?", (new_embedding, name))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def rename_face(self, old_name: str, new_name: str) -> bool:
        if self.face_exists(new_name):
            return False
        self.cursor.execute("UPDATE faces SET name = ? WHERE name = ?", (new_name, old_name))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def view_faces(self) -> list[str]:
        self.cursor.execute("SELECT name FROM faces")
        return [row[0] for row in self.cursor.fetchall()]

    def get_embedding_by_name(self, name: str):
        self.cursor.execute("SELECT embedding FROM faces WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def face_exists(self, name: str) -> bool:
        self.cursor.execute("SELECT 1 FROM faces WHERE name = ? LIMIT 1", (name,))
        return self.cursor.fetchone() is not None

    def get_all_embeddings(self) -> list[tuple[str, bytes]]:
        self.cursor.execute("SELECT name, embedding FROM faces")
        return self.cursor.fetchall()

    def add_attendance_record(self, name: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
        self.conn.commit()

    def get_attendance_records(self, name: Optional[str] = None, date: Optional[str] = None) -> list[
        tuple[int, str, str]]:
        """
        Retrieve attendance records, optionally filtered by name and date.
        Date format should be 'YYYY-MM-DD'.
        """
        query = "SELECT id, name, timestamp FROM attendance"
        conditions = []
        values = []

        if name:
            conditions.append("name = ?")
            values.append(name)
        if date:
            conditions.append("DATE(timestamp) = ?")
            values.append(date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC"

        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def get_attendance_records_with_id(self) -> list[tuple[int, str, str]]:
        self.cursor.execute("SELECT id, name, timestamp FROM attendance ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def delete_attendance_record_by_id(self, record_id: int) -> bool:
        self.cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def search_attendance(self, keyword: str) -> list[tuple[int, str, str]]:
        pattern = f"%{keyword}%"
        self.cursor.execute("""
            SELECT id, name, timestamp FROM attendance
            WHERE name LIKE ? OR timestamp LIKE ?
            ORDER BY timestamp DESC
        """, (pattern, pattern))
        return self.cursor.fetchall()

    def get_all_users(self) -> list[tuple[str, str]]:
        self.cursor.execute("SELECT username, role FROM users ORDER BY username ASC")
        return self.cursor.fetchall()

    def update_user_role(self, username: str, new_role: str) -> bool:
        self.cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_user_role(self, username: str, password: str) -> Optional[str]:
        self.cursor.execute(
            "SELECT role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def add_user(self, username: str, password: str, role: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()
