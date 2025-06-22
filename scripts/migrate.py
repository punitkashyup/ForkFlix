#!/usr/bin/env python3
"""
Database migration script for ForkFlix
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase', 'firebase-admin-key.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def create_indexes(db):
    """Create necessary Firestore indexes"""
    print("Creating Firestore indexes...")
    # Indexes are created via firestore.indexes.json
    print("Indexes configured in firestore.indexes.json")

def seed_data(db):
    """Seed initial data"""
    print("Seeding initial data...")
    
    # Add sample categories
    categories = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Snacks']
    for category in categories:
        db.collection('categories').add({
            'name': category,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    
    print("Initial data seeded successfully")

def main():
    """Main migration function"""
    try:
        db = initialize_firebase()
        create_indexes(db)
        seed_data(db)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()