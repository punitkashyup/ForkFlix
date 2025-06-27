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
    """Verify Firebase ID token - PRODUCTION MODE ONLY"""
    try:
        logger.info("🔍 Verifying Firebase token")
        
        if not credentials:
            logger.error("❌ No authentication credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if credentials.scheme.lower() != "bearer":
            logger.error(f"❌ Invalid authentication scheme: {credentials.scheme}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use Bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify Firebase token using Firebase Admin SDK
        try:
            import firebase_admin
            from firebase_admin import auth as firebase_auth
            
            # Initialize Firebase Admin if not already initialized
            if not firebase_admin._apps:
                import firebase_admin
                from firebase_admin import credentials as firebase_credentials
                logger.info("🔧 Initializing Firebase Admin SDK")
                firebase_admin.initialize_app()
            
            # Verify the Firebase ID token
            decoded_token = firebase_auth.verify_id_token(credentials.credentials)
            user_id = decoded_token.get('uid')
            
            if not user_id:
                logger.error("❌ No user ID found in token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user ID found"
                )
            
            logger.info(f"✅ Successfully verified token for user: {user_id}")
            return {
                "uid": user_id,
                "email": decoded_token.get('email', ''),
                "name": decoded_token.get('name', ''),
                "picture": decoded_token.get('picture', ''),
                "email_verified": decoded_token.get('email_verified', False),
                "firebase": decoded_token  # Include full token data
            }
            
        except firebase_admin.auth.InvalidIdTokenError:
            logger.error("❌ Invalid Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token"
            )
        except firebase_admin.auth.ExpiredIdTokenError:
            logger.error("❌ Expired Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired"
            )
        except Exception as firebase_error:
            logger.error(f"❌ Firebase authentication error: {firebase_error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication verification failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
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