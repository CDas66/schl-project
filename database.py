# database.py
import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.db_name = "library.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publisher TEXT,
                isbn TEXT UNIQUE,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Active'
            )
        ''')
        
        # Issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                member_id INTEGER,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                return_date TIMESTAMP,
                status TEXT DEFAULT 'Issued',
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (member_id) REFERENCES members (member_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Book operations
    def add_book(self, title, author, publisher, isbn, copies):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO books (title, author, publisher, isbn, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, author, publisher, isbn, copies, copies))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_books(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books ORDER BY book_id')
        books = cursor.fetchall()
        conn.close()
        return books
    
    def search_books(self, search_term):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        books = cursor.fetchall()
        conn.close()
        return books
    
    # Member operations
    def add_member(self, name, email, phone, address):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO members (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            ''', (name, email, phone, address))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_members(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members ORDER BY member_id')
        members = cursor.fetchall()
        conn.close()
        return members
    
    # Issue/Return operations
    def issue_book(self, book_id, member_id, days=14):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if book is available
        cursor.execute('SELECT available_copies FROM books WHERE book_id = ?', (book_id,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            due_date = datetime.now() + timedelta(days=days)
            cursor.execute('''
                INSERT INTO issues (book_id, member_id, due_date)
                VALUES (?, ?, ?)
            ''', (book_id, member_id, due_date))
            
            # Update available copies
            cursor.execute('''
                UPDATE books SET available_copies = available_copies - 1 
                WHERE book_id = ?
            ''', (book_id,))
            
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def return_book(self, issue_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get book_id from issue
        cursor.execute('SELECT book_id FROM issues WHERE issue_id = ?', (issue_id,))
        result = cursor.fetchone()
        
        if result:
            book_id = result[0]
            # Update issue record
            cursor.execute('''
                UPDATE issues SET return_date = CURRENT_TIMESTAMP, status = 'Returned'
                WHERE issue_id = ?
            ''', (issue_id,))
            
            # Update available copies
            cursor.execute('''
                UPDATE books SET available_copies = available_copies + 1 
                WHERE book_id = ?
            ''', (book_id,))
            
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def get_active_issues(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.issue_id, b.title, m.name, i.issue_date, i.due_date 
            FROM issues i
            JOIN books b ON i.book_id = b.book_id
            JOIN members m ON i.member_id = m.member_id
            WHERE i.status = 'Issued'
        ''')
        issues = cursor.fetchall()
        conn.close()
        return issues
    
    def search_members(self, search_term):
        """Search members by name, email, or phone"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM members 
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY member_id
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        members = cursor.fetchall()
        conn.close()
        return members
    
    def delete_member(self, member_id):
        """Delete a member if they have no active issues"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if member has active issues
        cursor.execute('''
            SELECT COUNT(*) FROM issues 
            WHERE member_id = ? AND status = 'Issued'
        ''', (member_id,))
        
        active_issues = cursor.fetchone()[0]
        
        if active_issues > 0:
            conn.close()
            return False
        
        # Delete member
        cursor.execute('DELETE FROM members WHERE member_id = ?', (member_id,))
        conn.commit()
        conn.close()
        return True
    
    def update_member_status(self, member_id, status):
        """Update member status (Active/Inactive)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE members SET status = ? WHERE member_id = ?
        ''', (status, member_id))
        conn.commit()
        conn.close()
        return True

    def get_member_by_id(self, member_id):
        """Get member details by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members WHERE member_id = ?', (member_id,))
        member = cursor.fetchone()
        conn.close()
        return member
    
    def get_book_by_id(self, book_id):
        """Get book details by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        book = cursor.fetchone()
        conn.close()
        return book
    
    def get_member_issues(self, member_id):
        """Get active issues for a member"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.issue_id, b.title, i.issue_date, i.due_date 
            FROM issues i
            JOIN books b ON i.book_id = b.book_id
            WHERE i.member_id = ? AND i.status = 'Issued'
        ''', (member_id,))
        issues = cursor.fetchall()
        conn.close()
        return issues
    
    def return_book(self, issue_id):
        """Process book return"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Get book_id from issue
            cursor.execute('SELECT book_id FROM issues WHERE issue_id = ?', (issue_id,))
            result = cursor.fetchone()
            
            if result:
                book_id = result[0]
                
                # Update issue record
                cursor.execute('''
                    UPDATE issues 
                    SET return_date = CURRENT_TIMESTAMP, status = 'Returned'
                    WHERE issue_id = ?
                ''', (issue_id,))
                
                # Update available copies
                cursor.execute('''
                    UPDATE books 
                    SET available_copies = available_copies + 1 
                    WHERE book_id = ?
                ''', (book_id,))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    def record_fine(self, issue_id, amount):
        """Record fine for overdue book"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Create fines table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fines (
                    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id INTEGER,
                    amount REAL,
                    paid_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Paid',
                    FOREIGN KEY (issue_id) REFERENCES issues (issue_id)
                )
            ''')
            
            cursor.execute('''
                INSERT INTO fines (issue_id, amount)
                VALUES (?, ?)
            ''', (issue_id, amount))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    def get_active_issues(self):
        """Get all active issues with book and member details"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                i.issue_id, 
                b.title, 
                m.name, 
                i.issue_date, 
                i.due_date,
                i.status
            FROM issues i
            JOIN books b ON i.book_id = b.book_id
            JOIN members m ON i.member_id = m.member_id
            WHERE i.status = 'Issued'
            ORDER BY i.due_date
        ''')
        issues = cursor.fetchall()
        conn.close()
        return issues
    
    