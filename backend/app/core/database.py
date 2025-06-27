import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self.db = None
        self.storage_bucket = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Firebase Admin SDK - PRODUCTION MODE ONLY"""
        if self.initialized:
            return
        
        try:
            # Check if Firebase credentials are available
            if not os.path.exists(settings.firebase_credentials_path):
                logger.error(f"❌ Firebase credentials file not found at {settings.firebase_credentials_path}")
                raise FileNotFoundError(f"Firebase credentials file is required: {settings.firebase_credentials_path}")
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(settings.firebase_credentials_path)
            
            # Check if Firebase app is already initialized
            try:
                firebase_admin.get_app()
                logger.info("✅ Firebase app already initialized")
            except ValueError:
                # App doesn't exist, initialize it
                firebase_admin.initialize_app(cred, {
                    'storageBucket': f"{settings.firebase_project_id}.appspot.com"
                })
                logger.info("✅ Firebase app initialized successfully")
            
            # Get Firestore client
            self.db = firestore.client()
            if not self.db:
                raise RuntimeError("Failed to create Firestore client")
            
            # Get Storage bucket
            self.storage_bucket = storage.bucket()
            if not self.storage_bucket:
                raise RuntimeError("Failed to create Firebase Storage bucket")
            
            self.initialized = True
            logger.info("✅ Firebase services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise RuntimeError(f"Firebase initialization failed: {e}")
    
    def get_db(self):
        """Get Firestore database client"""
        if not self.initialized:
            self.initialize()
        
        if not self.db:
            logger.error("❌ Firestore client not available")
            raise RuntimeError("Firestore database is not available")
            
        return self.db
    
    def get_storage(self):
        """Get Firebase Storage bucket"""
        if not self.initialized:
            self.initialize()
            
        if not self.storage_bucket:
            logger.error("❌ Firebase Storage not available")
            raise RuntimeError("Firebase Storage is not available")
            
        return self.storage_bucket

# Global Firebase service instance
firebase_service = FirebaseService()

def get_firestore_db():
    """Dependency to get Firestore database"""
    return firebase_service.get_db()

def get_firebase_storage():
    """Dependency to get Firebase Storage"""
    return firebase_service.get_storage()