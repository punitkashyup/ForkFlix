from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling - make it optional
security = HTTPBearer(auto_error=False)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

async def verify_firebase_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> dict:
    """Verify Firebase ID token"""
    try:
        logger.info(f"🔍 Token verification - Environment: {settings.environment}")
        logger.info(f"🔍 Credentials provided: {credentials is not None}")
        if credentials:
            logger.info(f"🔍 Token scheme: {credentials.scheme}")
            logger.info(f"🔍 Token preview: {credentials.credentials[:50]}...")
        
        # For development, if no token provided, return mock user
        if settings.environment == "development" and not credentials:
            logger.info("✅ Development mode: Using mock authentication (no token)")
            return {
                "uid": "dev_user_123",
                "email": "dev@example.com",
                "name": "Development User",
                "picture": None
            }
        
        # If credentials provided, try to verify
        if credentials:
            # For development, accept any token
            if settings.environment == "development":
                logger.info("✅ Development mode: Accepting provided token")
                return {
                    "uid": "firebase_user_from_token",
                    "email": "token@example.com", 
                    "name": "Token User",
                    "picture": None
                }
            
            # In production, uncomment and use this:
            # from firebase_admin import auth
            # decoded_token = auth.verify_id_token(credentials.credentials)
            # return decoded_token
        
        # Fallback mock user for development
        if settings.environment == "development":
            logger.info("✅ Development mode: Using fallback mock user")
            return {
                "uid": "mock_user_123",
                "email": "user@example.com",
                "name": "Mock User", 
                "picture": None
            }
        
        # In production, require authentication
        logger.error("❌ Production mode: Authentication required")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except HTTPException:
        logger.error("❌ HTTPException raised during token verification")
        raise
    except Exception as e:
        logger.error(f"❌ Token verification failed with exception: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        
        # In development, return mock user on error
        if settings.environment == "development":
            logger.warning("⚠️ Authentication failed, using mock user for development")
            return {
                "uid": "error_fallback_user",
                "email": "fallback@example.com",
                "name": "Fallback User",
                "picture": None
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None

async def get_current_user(token_data: dict = Depends(verify_firebase_token)) -> dict:
    """Get current authenticated user"""
    user_id = token_data.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data"
        )
    
    return {
        "uid": user_id,
        "email": token_data.get("email", ""),
        "name": token_data.get("name", ""),
        "picture": token_data.get("picture", "")
    }