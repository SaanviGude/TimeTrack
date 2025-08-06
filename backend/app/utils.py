from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESET_TOKEN_EXPIRE_MINUTES = 15  # Password reset tokens expire in 15 minutes

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def create_reset_token(email: str):
    """Create a password reset token for the given email"""
    expires_delta = timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_reset_token(token: str):
    """Verify password reset token and return email if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "password_reset":
            return None
        return email
    except JWTError:
        return None


def generate_secure_token(length: int = 32):
    """Generate a secure random token for additional security"""
    return secrets.token_urlsafe(length)
