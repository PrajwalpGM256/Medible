"""
Seed Data Script
Creates demo users with populated medications and search history
Run with: python seed_data.py
"""

import os
import sys

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.medication import UserMedication, SearchHistory
from datetime import datetime, timezone, timedelta

# Demo Users
DEMO_USERS = [
    {
        "email": "demo@medible.com",
        "password": "Demo123!",
        "first_name": "Alex",
        "last_name": "Johnson",
        "medications": [
            {"drug_name": "Lipitor", "brand_name": "Lipitor", "generic_name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily", "notes": "Take in the evening"},
            {"drug_name": "Lisinopril", "brand_name": "Zestril", "generic_name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "notes": "For blood pressure"},
            {"drug_name": "Metformin", "brand_name": "Glucophage", "generic_name": "Metformin", "dosage": "500mg", "frequency": "Twice daily", "notes": "Take with meals"},
        ],
        "searches": [
            {"food_name": "Grapefruit", "had_interaction": True},
            {"food_name": "Spinach", "had_interaction": False},
            {"food_name": "Banana", "had_interaction": True},
            {"food_name": "Coffee", "had_interaction": False},
            {"food_name": "Orange Juice", "had_interaction": True},
        ]
    },
    {
        "email": "john@example.com",
        "password": "John123!",
        "first_name": "John",
        "last_name": "Doe",
        "medications": [
            {"drug_name": "Warfarin", "brand_name": "Coumadin", "generic_name": "Warfarin", "dosage": "5mg", "frequency": "Once daily", "notes": "Blood thinner - watch vitamin K intake"},
            {"drug_name": "Aspirin", "brand_name": "Bayer", "generic_name": "Acetylsalicylic acid", "dosage": "81mg", "frequency": "Once daily", "notes": "Low-dose aspirin"},
        ],
        "searches": [
            {"food_name": "Kale", "had_interaction": True},
            {"food_name": "Broccoli", "had_interaction": True},
            {"food_name": "Chicken Breast", "had_interaction": False},
            {"food_name": "Rice", "had_interaction": False},
        ]
    },
    {
        "email": "sarah@example.com",
        "password": "Sarah123!",
        "first_name": "Sarah",
        "last_name": "Miller",
        "medications": [
            {"drug_name": "Synthroid", "brand_name": "Synthroid", "generic_name": "Levothyroxine", "dosage": "50mcg", "frequency": "Once daily", "notes": "Take on empty stomach"},
            {"drug_name": "Omeprazole", "brand_name": "Prilosec", "generic_name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "notes": "Take before breakfast"},
            {"drug_name": "Vitamin D", "brand_name": "Nature Made", "generic_name": "Cholecalciferol", "dosage": "2000 IU", "frequency": "Once daily", "notes": "Supplement"},
            {"drug_name": "Calcium", "brand_name": "Caltrate", "generic_name": "Calcium Carbonate", "dosage": "600mg", "frequency": "Twice daily", "notes": "Take with food"},
        ],
        "searches": [
            {"food_name": "Soy Milk", "had_interaction": True},
            {"food_name": "Walnuts", "had_interaction": True},
            {"food_name": "Yogurt", "had_interaction": False},
            {"food_name": "Apple", "had_interaction": False},
            {"food_name": "Green Tea", "had_interaction": True},
        ]
    },
    {
        "email": "mike@example.com", 
        "password": "Mike123!",
        "first_name": "Michael",
        "last_name": "Chen",
        "medications": [
            {"drug_name": "Ciprofloxacin", "brand_name": "Cipro", "generic_name": "Ciprofloxacin", "dosage": "500mg", "frequency": "Twice daily", "notes": "Antibiotic - avoid dairy"},
            {"drug_name": "Ibuprofen", "brand_name": "Advil", "generic_name": "Ibuprofen", "dosage": "400mg", "frequency": "As needed", "notes": "For pain relief"},
        ],
        "searches": [
            {"food_name": "Milk", "had_interaction": True},
            {"food_name": "Cheese", "had_interaction": True},
            {"food_name": "Salmon", "had_interaction": False},
        ]
    },
    {
        "email": "emma@example.com",
        "password": "Emma123!",
        "first_name": "Emma",
        "last_name": "Wilson",
        "medications": [
            {"drug_name": "Prozac", "brand_name": "Prozac", "generic_name": "Fluoxetine", "dosage": "20mg", "frequency": "Once daily", "notes": "Antidepressant"},
            {"drug_name": "Xanax", "brand_name": "Xanax", "generic_name": "Alprazolam", "dosage": "0.5mg", "frequency": "As needed", "notes": "For anxiety"},
            {"drug_name": "Birth Control", "brand_name": "Yaz", "generic_name": "Drospirenone/Ethinyl Estradiol", "dosage": "3mg/0.02mg", "frequency": "Once daily", "notes": "Take at same time each day"},
        ],
        "searches": [
            {"food_name": "Alcohol", "had_interaction": True},
            {"food_name": "Grapefruit Juice", "had_interaction": True},
            {"food_name": "Pasta", "had_interaction": False},
            {"food_name": "Avocado", "had_interaction": False},
        ]
    }
]


def seed_database():
    """Seed the database with demo data"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n🌱 Seeding Medible Database...")
        print("=" * 50)
        
        # Create tables if they don't exist
        db.create_all()
        
        users_created = 0
        medications_created = 0
        searches_created = 0
        
        for user_data in DEMO_USERS:
            # Check if user already exists
            existing = User.find_by_email(user_data["email"])
            if existing:
                print(f"⏭️  User {user_data['email']} already exists, skipping...")
                continue
            
            # Create user
            user = User(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"]
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            print(f"✅ Created user: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
            users_created += 1
            
            # Add medications
            for med_data in user_data.get("medications", []):
                medication = UserMedication(
                    user_id=user.id,
                    drug_name=med_data["drug_name"],
                    brand_name=med_data.get("brand_name"),
                    generic_name=med_data.get("generic_name"),
                    dosage=med_data.get("dosage"),
                    frequency=med_data.get("frequency"),
                    notes=med_data.get("notes"),
                    is_active=True
                )
                db.session.add(medication)
                medications_created += 1
            
            print(f"   💊 Added {len(user_data.get('medications', []))} medications")
            
            # Add search history
            for i, search_data in enumerate(user_data.get("searches", [])):
                # Stagger the search times
                search_time = datetime.now(timezone.utc) - timedelta(hours=i * 2, minutes=i * 15)
                
                search = SearchHistory(
                    user_id=user.id,
                    search_type="interaction",
                    search_term=search_data["food_name"],
                    had_interaction=search_data["had_interaction"],
                    results_count=1 if search_data["had_interaction"] else 0,
                    searched_at=search_time
                )
                db.session.add(search)
                searches_created += 1
            
            print(f"   🔍 Added {len(user_data.get('searches', []))} search history items")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 50)
        print(f"🎉 Seeding complete!")
        print(f"   👤 Users created: {users_created}")
        print(f"   💊 Medications created: {medications_created}")
        print(f"   🔍 Search history items: {searches_created}")
        print("\n📋 Demo Accounts:")
        print("-" * 50)
        for user_data in DEMO_USERS:
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print()


def clear_database():
    """Clear all data (use with caution!)"""
    app = create_app('development')
    
    with app.app_context():
        print("\n⚠️  Clearing all data...")
        
        # Delete in order to respect foreign keys
        SearchHistory.query.delete()
        UserMedication.query.delete()
        User.query.delete()
        
        db.session.commit()
        print("✅ Database cleared!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed the Medible database")
    parser.add_argument("--clear", action="store_true", help="Clear all data before seeding")
    parser.add_argument("--clear-only", action="store_true", help="Only clear data, don't seed")
    args = parser.parse_args()
    
    if args.clear_only:
        clear_database()
    elif args.clear:
        clear_database()
        seed_database()
    else:
        seed_database()
