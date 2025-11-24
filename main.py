import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self._init_db()

    # ---------------------- BASIC UTILITIES ----------------------
    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        """Create all tables if they do not already exist."""
        conn = self._connect()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS books (
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, author TEXT,
                        publisher TEXT, isbn TEXT UNIQUE,
                        total_copies INTEGER, available_copies INTEGER,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        c.execute('''CREATE TABLE IF NOT EXISTS members (
                        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT UNIQUE,
                        phone TEXT, address TEXT,
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Active')''')

        c.execute('''CREATE TABLE IF NOT EXISTS issues (
                        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER, member_id INTEGER,
                        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date TIMESTAMP, return_date TIMESTAMP,
                        status TEXT DEFAULT 'Issued',
                        FOREIGN KEY(book_id) REFERENCES books(book_id),
                        FOREIGN KEY(member_id) REFERENCES members(member_id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS fines (
                        fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        issue_id INTEGER, amount REAL,
                        paid_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Paid',
                        FOREIGN KEY(issue_id) REFERENCES issues(issue_id))''')

        conn.commit()
        conn.close()

    # ---------------------- BOOK OPERATIONS ----------------------
    def add_book(self, title, author, publisher, isbn, copies):
        conn = self._connect()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO books (title, author, publisher, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?, ?)",
                      (title, author, publisher, isbn, copies, copies))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_all_books(self):
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        data = c.fetchall()
        conn.close()
        return data

    def search_books(self, term):
        conn = self._connect()
        c = conn.cursor()
        like = f"%{term}%"
        c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?",
                  (like, like, like))
        data = c.fetchall()
        conn.close()
        return data

    # ---------------------- MEMBER OPERATIONS ----------------------
    def add_member(self, name, email, phone, address):
        conn = self._connect()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO members (name, email, phone, address) VALUES (?, ?, ?, ?)",
                      (name, email, phone, address))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_all_members(self):
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM members")
        data = c.fetchall()
        conn.close()
        return data

    def search_members(self, term):
        conn = self._connect()
        c = conn.cursor()
        like = f"%{term}%"
        c.execute("SELECT * FROM members WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?",
                  (like, like, like))
        data = c.fetchall()
        conn.close()
        return data

    def delete_member(self, member_id):
        conn = self._connect()
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM issues WHERE member_id=? AND status='Issued'", (member_id,))
        if c.fetchone()[0] > 0:
            conn.close()
            return False

        c.execute("DELETE FROM members WHERE member_id=?", (member_id,))
        conn.commit()
        conn.close()
        return True

    # ---------------------- ISSUE / RETURN ----------------------
    def issue_book(self, book_id, member_id, days=14):
        conn = self._connect()
        c = conn.cursor()

        c.execute("SELECT available_copies FROM books WHERE book_id=?", (book_id,))
        available = c.fetchone()

        if not available or available[0] <= 0:
            conn.close()
            return False

        due = datetime.now() + timedelta(days=days)
        c.execute("INSERT INTO issues (book_id, member_id, due_date) VALUES (?, ?, ?)",
                  (book_id, member_id, due))

        c.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=?",
                  (book_id,))

        conn.commit()
        conn.close()
        return True

    def return_book(self, issue_id):
        conn = self._connect()
        c = conn.cursor()

        c.execute("SELECT book_id FROM issues WHERE issue_id=?", (issue_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            return False

        book_id = row[0]

        c.execute("UPDATE issues SET return_date=CURRENT_TIMESTAMP, status='Returned' WHERE issue_id=?",
                  (issue_id,))
        c.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=?",
                  (book_id,))

        conn.commit()
        conn.close()
        return True

    def get_active_issues(self):
        conn = self._connect()
        c = conn.cursor()
        c.execute('''SELECT i.issue_id, b.title, m.name, i.issue_date, i.due_date, i.status
                     FROM issues i
                     JOIN books b ON i.book_id = b.book_id
                     JOIN members m ON i.member_id = m.member_id
                     WHERE i.status='Issued'
                     ORDER BY i.due_date''')
        data = c.fetchall()
        conn.close()
        return data

    # ---------------------- FINES ----------------------
    def record_fine(self, issue_id, amount):
        conn = self._connect()
        c = conn.cursor()

        c.execute("INSERT INTO fines (issue_id, amount) VALUES (?, ?)",
                  (issue_id, amount))

        conn.commit()
        conn.close()
        return True
