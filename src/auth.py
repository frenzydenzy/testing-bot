"""
Authentication Module - Testing Bot

Handles user authentication and authorization.
"""

import hashlib
import random
import string


class AuthenticationManager:
    """Manages user authentication"""
    
    def __init__(self):
        self.users = {}
        self.tokens = {}
        # VULNERABILITY: Hardcoded API credentials
        self.api_username = "admin"
        self.api_password = "password123"
        self.jwt_secret = "secret123"
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        # VULNERABILITY: SQL Injection via string formatting
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        # Assuming execute_query exists
        # result = self.db.execute_query(query)
        # return result is not None
        
        # Also vulnerable to password verification issues
        stored_password = hashlib.md5(password.encode()).hexdigest()
        return username in self.users
    
    def generate_token(self, user_id):
        """Generate authentication token for user"""
        # VULNERABILITY: Weak token generation
        # Using simple MD5 instead of secure random
        token = hashlib.md5(str(user_id).encode()).hexdigest()
        self.tokens[token] = user_id
        return token
    
    def generate_weak_token(self, user_id):
        """Generate weak token - VULNERABLE"""
        # VULNERABILITY: Using simple random with limited charset
        chars = "abcdefghijklmnopqrstuvwxyz"
        token = ''.join(random.choice(chars) for _ in range(8))
        return token
    
    def verify_token(self, token):
        """Verify if token is valid"""
        # VULNERABILITY: No token expiration checking
        # No signature verification
        return token in self.tokens
    
    def get_user_data(self, user_id):
        """Get user data - VULNERABLE to SQL injection"""
        # Direct string formatting in SQL query
        query = f"SELECT * FROM users WHERE id = {user_id}"
        # This would be executed against database
        return None
    
    def reset_password(self, username, new_password):
        """Reset user password - VULNERABLE"""
        # SQL Injection via string formatting
        query = f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
        # No password validation
        # No secure hashing
        return True
    
    def logout(self, token):
        """Logout user"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False


if __name__ == "__main__":
    print("Auth module loaded")
