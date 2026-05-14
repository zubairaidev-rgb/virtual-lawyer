"""
Security utilities for the Lawmate API: JWT issuance/verification, HTML sanitization,
and FastAPI dependencies for role-based access control (RBAC).

Used by ``api_complete`` for login responses and protected admin/lawyer routes.
When optional dependencies (``python-jose``, ``bleach``, …) are missing, the API
falls back to development stubs defined in ``api_complete``.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bleach import clean

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "lawmate-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)  # auto_error=False to handle missing tokens gracefully


# ============================================================
# INPUT SANITIZATION
# ============================================================

def sanitize_html(text: str) -> str:
    """
    Remove all HTML tags and dangerous characters to prevent XSS attacks.

    Args:
        text: Input string that may contain HTML/scripts

    Returns:
        Sanitized string safe for storage and display
    """
    if not text or not isinstance(text, str):
        return text

    # Remove all HTML tags
    sanitized = clean(text, tags=[], attributes={}, strip=True)

    # Also escape special characters as extra protection
    sanitized = (
        sanitized.replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;')
    )

    return sanitized


def sanitize_dict(data: dict, fields: list) -> dict:
    """
    Sanitize specific fields in a dictionary.

    Args:
        data: Dictionary containing user input
        fields: List of field names to sanitize

    Returns:
        Dictionary with sanitized fields
    """
    sanitized = data.copy()
    for field in fields:
        if field in sanitized and isinstance(sanitized[field], str):
            sanitized[field] = sanitize_html(sanitized[field])
    return sanitized


# ============================================================
# JWT TOKEN MANAGEMENT
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user data (user_id, role, etc.)
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if token has expired
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {str(e)}"
        )


# ============================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    Dependency to get current authenticated user from JWT token.

    Can be used as: current_user = Depends(get_current_user)

    Returns:
        Dictionary with user info: {"sub": user_id, "role": user_role, ...}

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid token."
        )

    token = credentials.credentials
    return verify_token(token)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Optional authentication - returns user if authenticated, None otherwise.

    Useful for endpoints that work differently for authenticated vs anonymous users.
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        return verify_token(token)
    except HTTPException:
        return None


# ============================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================

def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Usage:
        @app.get("/api/lawyer/clients")
        async def get_clients(current_user = Depends(require_role("lawyer"))):
            pass

    Args:
        required_role: Required user role ("admin", "lawyer", "citizen")

    Returns:
        Dependency function that enforces role requirement
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. {required_role.capitalize()} privileges required."
            )

        return current_user

    return role_checker


def require_any_role(allowed_roles: list):
    """
    Dependency factory for multiple allowed roles.

    Usage:
        @app.get("/api/cases")
        async def get_cases(current_user = Depends(require_any_role(["lawyer", "citizen"]))):
            pass

    Args:
        allowed_roles: List of allowed roles

    Returns:
        Dependency function that enforces role requirement
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. One of these roles required: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker


# ============================================================
# OWNERSHIP VERIFICATION
# ============================================================

def verify_ownership(current_user: dict, resource_user_id: str):
    """
    Verify that the current user owns the resource they're trying to access.

    Use this to prevent horizontal privilege escalation (user A accessing user B's data).

    Args:
        current_user: Current authenticated user dict
        resource_user_id: User ID that owns the resource

    Raises:
        HTTPException: 403 if user doesn't own the resource
    """
    if current_user.get("sub") != resource_user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own data."
        )


def verify_ownership_or_admin(current_user: dict, resource_user_id: str):
    """
    Verify that user owns resource OR is an admin.

    Args:
        current_user: Current authenticated user dict
        resource_user_id: User ID that owns the resource

    Raises:
        HTTPException: 403 if user doesn't own resource and isn't admin
    """
    user_id = current_user.get("sub")
    user_role = current_user.get("role")

    if user_id != resource_user_id and user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own data."
        )


# ============================================================
# LEGACY HEADER-BASED AUTH (For backwards compatibility)
# ============================================================

async def get_user_from_headers(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_type: Optional[str] = Header(None, alias="X-User-Type")
) -> Optional[Dict]:
    """
    Legacy header-based authentication (backwards compatibility).
    NOT RECOMMENDED for production - use JWT tokens instead.
    """
    if x_user_id and x_user_type:
        return {
            "sub": x_user_id,
            "role": x_user_type,
            "legacy": True
        }
    return None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_user_token_response(user: dict, user_type: str) -> dict:
    """
    Create a standardized login response with JWT token.

    Args:
        user: User data dictionary
        user_type: User type ("admin", "lawyer", "citizen")

    Returns:
        Response dict with access_token and user info
    """
    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user.get("id") or user.get("_id"),
            "role": user_type,
            "email": user.get("email")
        }
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "message": "Login successful"
    }
