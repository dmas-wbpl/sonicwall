import hashlib
import os
import time
from typing import Optional
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.services import user_service

# Constants for digest auth
REALM = "sonicwall_api"
ALGORITHM = "SHA-256"
QOP = "auth"
NONCE_BYTES = 32

def generate_nonce() -> str:
    """Generate a random nonce for digest authentication."""
    return hashlib.sha256(os.urandom(NONCE_BYTES)).hexdigest()

def generate_digest_challenge() -> str:
    """Generate a digest authentication challenge."""
    nonce = generate_nonce()
    return f'Digest realm="{REALM}", nonce="{nonce}", algorithm={ALGORITHM}, qop="{QOP}"'

def calculate_ha1(username: str, password: str) -> str:
    """Calculate HA1 = MD5(username:realm:password)"""
    return hashlib.sha256(f"{username}:{REALM}:{password}".encode()).hexdigest()

def calculate_ha2(method: str, uri: str) -> str:
    """Calculate HA2 = MD5(method:uri)"""
    return hashlib.sha256(f"{method}:{uri}".encode()).hexdigest()

def calculate_response(ha1: str, nonce: str, nc: str, cnonce: str, qop: str, ha2: str) -> str:
    """Calculate response = MD5(HA1:nonce:nc:cnonce:qop:HA2)"""
    return hashlib.sha256(
        f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()
    ).hexdigest()

def verify_digest_auth(credentials: HTTPAuthorizationCredentials, db: Session) -> Optional[dict]:
    """
    Verify the digest authentication credentials.
    Returns the user if authentication is successful, None otherwise.
    """
    if not credentials or not credentials.credentials:
        return None

    # Parse the authorization header
    auth_dict = dict(
        item.split("=", 1) for item in credentials.credentials[7:].split(",")
    )
    
    # Clean up the parsed values
    for key in auth_dict:
        auth_dict[key] = auth_dict[key].strip().strip('"')

    # Get user from database
    user = user_service.get_user_by_username(db, auth_dict.get("username"))
    if not user:
        return None

    # Calculate expected response
    ha1 = calculate_ha1(user.username, user.password)
    ha2 = calculate_ha2(auth_dict.get("method", "GET"), auth_dict.get("uri", "/"))
    
    expected_response = calculate_response(
        ha1,
        auth_dict.get("nonce"),
        auth_dict.get("nc"),
        auth_dict.get("cnonce"),
        auth_dict.get("qop"),
        ha2
    )

    if auth_dict.get("response") == expected_response:
        return user
    
    return None 