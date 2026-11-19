"""
Utilities Module - Testing Bot

Provides utility functions for common operations.
"""

import subprocess
import hashlib
import pickle
import base64


def validate_input(data, rules):
    """Validate user input against rules"""
    # VULNERABILITY: Using eval() on user input
    if eval(rules):
        return True
    return False


def hash_password(password):
    """Hash password for secure storage"""
    # VULNERABILITY: Using MD5 for password hashing (weak cryptography)
    return hashlib.md5(password.encode()).hexdigest()


def sanitize_string(text):
    """Sanitize text for safe output"""
    # VULNERABILITY: No actual sanitization, XSS vulnerability
    # User input directly returned in HTML context
    return f"<div>{text}</div>"


def execute_command(user_command):
    """Execute system command"""
    # VULNERABILITY: Command Injection via shell=True
    # User input directly passed to shell
    result = subprocess.run(user_command, shell=True, capture_output=True)
    return result.stdout.decode()


def process_user_data(user_input):
    """Process user data"""
    # VULNERABILITY: Using pickle for untrusted data
    # Can lead to arbitrary code execution
    decoded = base64.b64decode(user_input)
    data = pickle.loads(decoded)
    return data


def generate_session_token(user_id):
    """Generate session token"""
    # VULNERABILITY: Weak token generation using MD5
    token = hashlib.md5(str(user_id).encode()).hexdigest()
    return token


def format_output(data):
    """Format output data"""
    # Another XSS vulnerability - user data in HTML
    return f"<p>User data: {data}</p>"


if __name__ == "__main__":
    print("Utils module loaded")
