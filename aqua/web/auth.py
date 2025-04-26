import os
import json
import uuid
import hashlib
import secrets
import datetime
from typing import Optional, Dict, List
from pathlib import Path

# Constants
AUTH_DIR = Path(__file__).parent / "data" / "auth"
USERS_FILE = AUTH_DIR / "users.json"
SESSIONS_FILE = AUTH_DIR / "sessions.json"
RESET_TOKENS_FILE = AUTH_DIR / "reset_tokens.json"

# Ensure data directories exist
os.makedirs(AUTH_DIR, exist_ok=True)

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """Hash a password with salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    pw_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return pw_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify a password against a stored hash."""
    calculated_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calculated_hash, stored_hash)

def load_users() -> List[Dict]:
    """Load users from the users file."""
    if not USERS_FILE.exists():
        return []
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users: List[Dict]) -> None:
    """Save users to the users file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def find_user(username_or_email: str) -> Optional[Dict]:
    """Find a user by username or email."""
    users = load_users()
    
    for user in users:
        if user["username"].lower() == username_or_email.lower() or user.get("email", "").lower() == username_or_email.lower():
            return user
    
    return None

def register_user(username: str, password: str, email: str, full_name: str) -> Dict:
    """Register a new user."""
    users = load_users()
    
    # Check if username or email already exists
    for user in users:
        if user["username"].lower() == username.lower():
            raise ValueError("Username already exists")
        
        if user.get("email", "").lower() == email.lower():
            raise ValueError("Email already exists")
    
    # Hash the password
    password_hash, salt = hash_password(password)
    
    # Create new user
    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "full_name": full_name,
        "password_hash": password_hash,
        "salt": salt,
        "role": "user",
        "created_at": datetime.datetime.now().isoformat(),
        "last_login": None
    }
    
    users.append(user)
    save_users(users)
    
    # Return user without sensitive info
    return {k: v for k, v in user.items() if k not in ["password_hash", "salt"]}

def authenticate_user(username_or_email: str, password: str) -> Optional[Dict]:
    """Authenticate a user."""
    user = find_user(username_or_email)
    
    if not user:
        return None
    
    if verify_password(password, user["password_hash"], user["salt"]):
        # Update last login time
        users = load_users()
        
        for u in users:
            if u["id"] == user["id"]:
                u["last_login"] = datetime.datetime.now().isoformat()
                break
        
        save_users(users)
        
        # Return user without sensitive info
        return {k: v for k, v in user.items() if k not in ["password_hash", "salt"]}
    
    return None

def create_session(user_id: str, remember: bool = False) -> str:
    """Create a new session for a user."""
    session_id = secrets.token_urlsafe(32)
    
    if not SESSIONS_FILE.exists():
        sessions = []
    else:
        try:
            with open(SESSIONS_FILE, 'r') as f:
                sessions = json.load(f)
        except:
            sessions = []
    
    # Calculate expiry time - 30 days if remember me is checked, otherwise 1 day
    expiry = (datetime.datetime.now() + 
             (datetime.timedelta(days=30) if remember else datetime.timedelta(days=1))).isoformat()
    
    session = {
        "id": session_id,
        "user_id": user_id,
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": expiry
    }
    
    sessions.append(session)
    
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)
    
    return session_id

def get_session(session_id: str) -> Optional[Dict]:
    """Get session details by session ID."""
    if not SESSIONS_FILE.exists():
        return None
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
            
        for session in sessions:
            if session["id"] == session_id:
                # Check if session has expired
                expiry_time = datetime.datetime.fromisoformat(session["expires_at"])
                if expiry_time > datetime.datetime.now():
                    return session
                
                # Session expired
                delete_session(session_id)
                return None
    except:
        pass
    
    return None

def delete_session(session_id: str) -> None:
    """Delete a session."""
    if not SESSIONS_FILE.exists():
        return
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
            
        sessions = [s for s in sessions if s["id"] != session_id]
        
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    except:
        pass

def create_password_reset_token(email: str) -> Optional[str]:
    """Create a password reset token for a user."""
    user = find_user(email)
    
    if not user:
        return None
    
    token = secrets.token_urlsafe(32)
    
    if not RESET_TOKENS_FILE.exists():
        reset_tokens = []
    else:
        try:
            with open(RESET_TOKENS_FILE, 'r') as f:
                reset_tokens = json.load(f)
        except:
            reset_tokens = []
    
    # Token valid for 24 hours
    expiry = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    
    reset_token = {
        "token": token,
        "user_id": user["id"],
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": expiry,
        "used": False
    }
    
    reset_tokens.append(reset_token)
    
    with open(RESET_TOKENS_FILE, 'w') as f:
        json.dump(reset_tokens, f, indent=2)
    
    return token

def verify_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return user_id if valid."""
    if not RESET_TOKENS_FILE.exists():
        return None
    
    try:
        with open(RESET_TOKENS_FILE, 'r') as f:
            reset_tokens = json.load(f)
            
        for reset_token in reset_tokens:
            if reset_token["token"] == token and not reset_token["used"]:
                # Check if token has expired
                expiry_time = datetime.datetime.fromisoformat(reset_token["expires_at"])
                if expiry_time > datetime.datetime.now():
                    return reset_token["user_id"]
                
                # Token expired
                return None
    except:
        pass
    
    return None

def reset_password(token: str, new_password: str) -> bool:
    """Reset a user's password using a token."""
    user_id = verify_reset_token(token)
    
    if not user_id:
        return False
    
    # Mark token as used
    with open(RESET_TOKENS_FILE, 'r') as f:
        reset_tokens = json.load(f)
    
    for reset_token in reset_tokens:
        if reset_token["token"] == token:
            reset_token["used"] = True
            break
    
    with open(RESET_TOKENS_FILE, 'w') as f:
        json.dump(reset_tokens, f, indent=2)
    
    # Update user password
    users = load_users()
    
    for user in users:
        if user["id"] == user_id:
            password_hash, salt = hash_password(new_password)
            user["password_hash"] = password_hash
            user["salt"] = salt
            save_users(users)
            return True
    
    return False

def create_demo_user():
    """Create a demo user for testing"""
    users = load_users()
    if not users:
        try:
            register_user(
                username="admin",
                password="admin123",  # In production, use a strong password
                email="admin@example.com",
                full_name="Admin User"
            )
            print("Demo admin user created successfully")
        except Exception as e:
            print(f"Error creating demo user: {e}")

def get_current_user(session: Optional[str] = None):
    """Get the current user based on session token"""
    if not session:
        return None

    session_data = get_session(session)
    if not session_data:
        return None

    user = find_user(session_data["user_id"])
    return user

def validate_login(username: str, password: str) -> bool:
    """Validate login credentials"""
    user = find_user(username)
    if user and verify_password(password, user["password_hash"], user["salt"]):
        return True
    return False
