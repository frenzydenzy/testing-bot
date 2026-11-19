"""
Database Module - Testing Bot

Handles all database operations.
Currently a placeholder for testing remediation agent.
"""

import sqlite3
import os


class DatabaseConnection:
    """Database connection handler"""
    
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        # Hardcoded database credentials - VULNERABILITY: Hardcoded Secrets
        self.db_username = "admin"
        self.db_password = "admin123456"
        self.api_key = "sk_live_abcdef123456789xyz"
        self.aws_secret = "AKIAIOSFODNN7EXAMPLE"
    
    def connect(self):
        """Establish database connection"""
        # Simple connection to database
        self.connection = sqlite3.connect(':memory:')
    
    def execute_query(self, query):
        """Execute database query"""
        # VULNERABILITY: SQL Injection - directly using user input in query
        if self.connection:
            cursor = self.connection.cursor()
            # This is vulnerable to SQL injection
            cursor.execute(query)
            return cursor.fetchall()
    
    def fetch_data(self, table, filters=None):
        """Fetch data from table"""
        # VULNERABILITY: SQL Injection via string formatting
        if filters:
            query = f"SELECT * FROM {table} WHERE {filters}"
        else:
            query = f"SELECT * FROM {table}"
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_user(self, user_id):
        """Get user by ID - VULNERABLE to SQL injection"""
        # Direct string concatenation - SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    
    def login_user(self, username, password):
        """Login user - VULNERABLE to SQL injection"""
        # Using f-string for SQL query - SQL Injection vulnerability
        query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result is not None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    print("Database module loaded")
