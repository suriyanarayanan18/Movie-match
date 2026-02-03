import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

class Database:
    def __init__(self, db_name='moviematch.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Create a database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                rating REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # User badges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                badge_description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, badge_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    @staticmethod
    def hash_password(password):
        """Hash a password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password):
        """Create a new user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_pw = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, user_id
        except sqlite3.IntegrityError:
            conn.close()
            return False, None
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return their user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed_pw = self.hash_password(password)
        cursor.execute(
            "SELECT id, username FROM users WHERE username=? AND password=?",
            (username, hashed_pw)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, user[0], user[1]  # success, user_id, username
        return False, None, None
    
    def add_rating(self, user_id, movie_id, rating):
        """Add or update a user's rating for a movie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT INTO user_ratings (user_id, movie_id, rating) 
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, movie_id) 
                   DO UPDATE SET rating=?, created_at=CURRENT_TIMESTAMP''',
                (user_id, movie_id, rating, rating)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error adding rating: {e}")
            return False
    
    def get_user_ratings(self, user_id):
        """Get all ratings for a specific user"""
        conn = self.get_connection()
        query = '''
            SELECT movie_id, rating, created_at 
            FROM user_ratings 
            WHERE user_id = ?
            ORDER BY created_at DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df
    
    def get_user_rating_for_movie(self, user_id, movie_id):
        """Check if user has rated a specific movie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating FROM user_ratings WHERE user_id=? AND movie_id=?",
            (user_id, movie_id)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_badge(self, user_id, badge_name, badge_description):
        """Award a badge to a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''INSERT INTO user_badges (user_id, badge_name, badge_description)
                   VALUES (?, ?, ?)''',
                (user_id, badge_name, badge_description)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Badge already exists for this user
            conn.close()
            return False
    
    def get_user_badges(self, user_id):
        """Get all badges for a user"""
        conn = self.get_connection()
        query = '''
            SELECT badge_name, badge_description, earned_at
            FROM user_badges
            WHERE user_id = ?
            ORDER BY earned_at DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df
    
    def get_all_users_with_ratings(self):
        """Get all users who have rated at least one movie"""
        conn = self.get_connection()
        query = '''
            SELECT DISTINCT u.id, u.username, COUNT(ur.id) as rating_count
            FROM users u
            INNER JOIN user_ratings ur ON u.id = ur.user_id
            GROUP BY u.id, u.username
            HAVING rating_count > 0
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


# Test the database
if __name__ == "__main__":
    db = Database()
    print("Database setup complete!")
    