"""
Seed Data Script
Creates demo users with populated medications and search history
Run with: python seed_data.py
"""

import os
import sys
import json

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.medication import UserMedication, SearchHistory, FoodLog, InteractionCheck
from datetime import datetime, timezone, timedelta, date

# Demo Users with comprehensive data
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
            {"drug_name": "Warfarin", "brand_name": "Coumadin", "generic_name": "Warfarin", "dosage": "5mg", "frequency": "Once daily", "notes": "Blood thinner - monitor vitamin K"},
            {"drug_name": "Omeprazole", "brand_name": "Prilosec", "generic_name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "notes": "Take before breakfast"},
            {"drug_name": "Amlodipine", "brand_name": "Norvasc", "generic_name": "Amlodipine", "dosage": "5mg", "frequency": "Once daily", "notes": "Calcium channel blocker"},
            {"drug_name": "Levothyroxine", "brand_name": "Synthroid", "generic_name": "Levothyroxine", "dosage": "50mcg", "frequency": "Once daily", "notes": "Take on empty stomach"},
            {"drug_name": "Metoprolol", "brand_name": "Lopressor", "generic_name": "Metoprolol", "dosage": "25mg", "frequency": "Twice daily", "notes": "Beta blocker for heart"},
        ],
        "searches": [
            {"food_name": "Grapefruit", "had_interaction": True},
            {"food_name": "Spinach", "had_interaction": True},
            {"food_name": "Banana", "had_interaction": False},
            {"food_name": "Coffee", "had_interaction": True},
            {"food_name": "Orange Juice", "had_interaction": False},
            {"food_name": "Kale", "had_interaction": True},
            {"food_name": "Broccoli", "had_interaction": True},
            {"food_name": "Green Tea", "had_interaction": True},
            {"food_name": "Alcohol", "had_interaction": True},
            {"food_name": "Milk", "had_interaction": False},
            {"food_name": "Cheese", "had_interaction": False},
            {"food_name": "Salmon", "had_interaction": False},
        ],
        "food_diary": [
            # Today's meals
            {"food_name": "Scrambled Eggs", "meal_type": "breakfast", "servings": 2, "calories": 180, "protein": 12, "carbs": 2, "fat": 14, "days_ago": 0},
            {"food_name": "Whole Wheat Toast", "meal_type": "breakfast", "servings": 2, "calories": 140, "protein": 6, "carbs": 26, "fat": 2, "days_ago": 0},
            {"food_name": "Black Coffee", "meal_type": "breakfast", "servings": 1, "calories": 5, "protein": 0, "carbs": 0, "fat": 0, "days_ago": 0},
            {"food_name": "Grilled Chicken Breast", "meal_type": "lunch", "servings": 1, "calories": 165, "protein": 31, "carbs": 0, "fat": 4, "days_ago": 0},
            {"food_name": "Brown Rice", "meal_type": "lunch", "servings": 1, "calories": 215, "protein": 5, "carbs": 45, "fat": 2, "days_ago": 0},
            {"food_name": "Steamed Broccoli", "meal_type": "lunch", "servings": 1, "calories": 55, "protein": 4, "carbs": 11, "fat": 1, "days_ago": 0},
            {"food_name": "Apple", "meal_type": "snack", "servings": 1, "calories": 95, "protein": 0, "carbs": 25, "fat": 0, "days_ago": 0},
            {"food_name": "Almonds", "meal_type": "snack", "servings": 1, "calories": 160, "protein": 6, "carbs": 6, "fat": 14, "days_ago": 0},
            {"food_name": "Salmon Fillet", "meal_type": "dinner", "servings": 1, "calories": 280, "protein": 36, "carbs": 0, "fat": 14, "days_ago": 0},
            {"food_name": "Quinoa", "meal_type": "dinner", "servings": 1, "calories": 220, "protein": 8, "carbs": 39, "fat": 4, "days_ago": 0},
            {"food_name": "Mixed Green Salad", "meal_type": "dinner", "servings": 1, "calories": 45, "protein": 2, "carbs": 8, "fat": 0, "days_ago": 0},
            # Yesterday's meals
            {"food_name": "Oatmeal with Berries", "meal_type": "breakfast", "servings": 1, "calories": 220, "protein": 6, "carbs": 40, "fat": 4, "days_ago": 1},
            {"food_name": "Greek Yogurt", "meal_type": "breakfast", "servings": 1, "calories": 130, "protein": 15, "carbs": 8, "fat": 4, "days_ago": 1},
            {"food_name": "Turkey Sandwich", "meal_type": "lunch", "servings": 1, "calories": 350, "protein": 28, "carbs": 35, "fat": 10, "days_ago": 1},
            {"food_name": "Carrot Sticks", "meal_type": "snack", "servings": 1, "calories": 35, "protein": 1, "carbs": 8, "fat": 0, "days_ago": 1},
            {"food_name": "Grilled Salmon", "meal_type": "dinner", "servings": 1, "calories": 300, "protein": 40, "carbs": 0, "fat": 14, "days_ago": 1},
            {"food_name": "Roasted Vegetables", "meal_type": "dinner", "servings": 1, "calories": 120, "protein": 3, "carbs": 20, "fat": 4, "days_ago": 1},
            # 2 days ago
            {"food_name": "Avocado Toast", "meal_type": "breakfast", "servings": 1, "calories": 280, "protein": 7, "carbs": 25, "fat": 18, "days_ago": 2},
            {"food_name": "Caesar Salad", "meal_type": "lunch", "servings": 1, "calories": 320, "protein": 18, "carbs": 12, "fat": 22, "days_ago": 2},
            {"food_name": "Protein Bar", "meal_type": "snack", "servings": 1, "calories": 200, "protein": 20, "carbs": 18, "fat": 8, "days_ago": 2},
            {"food_name": "Pasta Primavera", "meal_type": "dinner", "servings": 1, "calories": 420, "protein": 14, "carbs": 65, "fat": 12, "days_ago": 2},
            # 3 days ago
            {"food_name": "Smoothie Bowl", "meal_type": "breakfast", "servings": 1, "calories": 350, "protein": 8, "carbs": 55, "fat": 12, "days_ago": 3},
            {"food_name": "Chicken Wrap", "meal_type": "lunch", "servings": 1, "calories": 380, "protein": 32, "carbs": 28, "fat": 16, "days_ago": 3},
            {"food_name": "Mixed Nuts", "meal_type": "snack", "servings": 1, "calories": 180, "protein": 5, "carbs": 6, "fat": 16, "days_ago": 3},
            {"food_name": "Steak", "meal_type": "dinner", "servings": 1, "calories": 400, "protein": 42, "carbs": 0, "fat": 25, "days_ago": 3},
            {"food_name": "Baked Potato", "meal_type": "dinner", "servings": 1, "calories": 160, "protein": 4, "carbs": 37, "fat": 0, "days_ago": 3},
        ],
        "interaction_checks": [
            {"food_name": "Grapefruit", "had_interaction": True, "interaction_count": 2, "max_severity": "high", "hours_ago": 2,
             "medications": ["Lipitor", "Amlodipine"],
             "interactions": [
                 {"drugName": "Lipitor", "foodName": "Grapefruit", "severity": "high", "effect": "Grapefruit can significantly increase blood levels of atorvastatin, increasing risk of muscle damage.", "recommendation": "Avoid grapefruit and grapefruit juice while taking Lipitor."},
                 {"drugName": "Amlodipine", "foodName": "Grapefruit", "severity": "moderate", "effect": "Grapefruit may increase amlodipine levels in blood.", "recommendation": "Limit grapefruit intake or consult your doctor."}
             ]},
            {"food_name": "Spinach", "had_interaction": True, "interaction_count": 1, "max_severity": "high", "hours_ago": 8,
             "medications": ["Warfarin"],
             "interactions": [
                 {"drugName": "Warfarin", "foodName": "Spinach", "severity": "high", "effect": "High vitamin K content can reduce warfarin effectiveness.", "recommendation": "Maintain consistent vitamin K intake daily."}
             ]},
            {"food_name": "Banana", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 12,
             "medications": ["Lipitor", "Lisinopril", "Metformin"], "interactions": []},
            {"food_name": "Coffee", "had_interaction": True, "interaction_count": 1, "max_severity": "low", "hours_ago": 24,
             "medications": ["Levothyroxine"],
             "interactions": [
                 {"drugName": "Levothyroxine", "foodName": "Coffee", "severity": "low", "effect": "Coffee may reduce absorption of levothyroxine.", "recommendation": "Wait 30-60 minutes after taking medication before drinking coffee."}
             ]},
            {"food_name": "Kale", "had_interaction": True, "interaction_count": 1, "max_severity": "high", "hours_ago": 36,
             "medications": ["Warfarin"],
             "interactions": [
                 {"drugName": "Warfarin", "foodName": "Kale", "severity": "high", "effect": "Very high vitamin K content can significantly reduce warfarin effectiveness.", "recommendation": "Limit kale intake and maintain consistency."}
             ]},
            {"food_name": "Orange Juice", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 48,
             "medications": ["Lipitor", "Metformin"], "interactions": []},
            {"food_name": "Alcohol", "had_interaction": True, "interaction_count": 2, "max_severity": "high", "hours_ago": 72,
             "medications": ["Metformin", "Warfarin"],
             "interactions": [
                 {"drugName": "Metformin", "foodName": "Alcohol", "severity": "high", "effect": "Alcohol can increase risk of lactic acidosis with metformin.", "recommendation": "Limit alcohol consumption significantly."},
                 {"drugName": "Warfarin", "foodName": "Alcohol", "severity": "moderate", "effect": "Alcohol can enhance warfarin's blood-thinning effect.", "recommendation": "Limit to 1-2 drinks occasionally."}
             ]},
            {"food_name": "Cheese", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 96,
             "medications": ["Lipitor", "Lisinopril"], "interactions": []},
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
            {"drug_name": "Metoprolol", "brand_name": "Lopressor", "generic_name": "Metoprolol", "dosage": "50mg", "frequency": "Twice daily", "notes": "For heart rate control"},
        ],
        "searches": [
            {"food_name": "Kale", "had_interaction": True},
            {"food_name": "Broccoli", "had_interaction": True},
            {"food_name": "Chicken Breast", "had_interaction": False},
            {"food_name": "Rice", "had_interaction": False},
            {"food_name": "Cranberry Juice", "had_interaction": True},
            {"food_name": "Spinach Salad", "had_interaction": True},
        ],
        "food_diary": [
            {"food_name": "Bacon and Eggs", "meal_type": "breakfast", "servings": 1, "calories": 350, "protein": 22, "carbs": 2, "fat": 28, "days_ago": 0},
            {"food_name": "Orange Juice", "meal_type": "breakfast", "servings": 1, "calories": 110, "protein": 2, "carbs": 26, "fat": 0, "days_ago": 0},
            {"food_name": "BLT Sandwich", "meal_type": "lunch", "servings": 1, "calories": 420, "protein": 18, "carbs": 32, "fat": 26, "days_ago": 0},
            {"food_name": "Banana", "meal_type": "snack", "servings": 1, "calories": 105, "protein": 1, "carbs": 27, "fat": 0, "days_ago": 0},
            {"food_name": "Pork Chops", "meal_type": "dinner", "servings": 1, "calories": 290, "protein": 38, "carbs": 0, "fat": 14, "days_ago": 0},
            {"food_name": "Mashed Potatoes", "meal_type": "dinner", "servings": 1, "calories": 180, "protein": 4, "carbs": 36, "fat": 3, "days_ago": 0},
            {"food_name": "Pancakes", "meal_type": "breakfast", "servings": 2, "calories": 280, "protein": 6, "carbs": 48, "fat": 8, "days_ago": 1},
            {"food_name": "Maple Syrup", "meal_type": "breakfast", "servings": 1, "calories": 100, "protein": 0, "carbs": 26, "fat": 0, "days_ago": 1},
            {"food_name": "Hamburger", "meal_type": "lunch", "servings": 1, "calories": 540, "protein": 28, "carbs": 40, "fat": 30, "days_ago": 1},
            {"food_name": "Spaghetti Bolognese", "meal_type": "dinner", "servings": 1, "calories": 480, "protein": 24, "carbs": 58, "fat": 18, "days_ago": 1},
        ],
        "interaction_checks": [
            {"food_name": "Kale", "had_interaction": True, "interaction_count": 1, "max_severity": "high", "hours_ago": 6,
             "medications": ["Warfarin"],
             "interactions": [
                 {"drugName": "Warfarin", "foodName": "Kale", "severity": "high", "effect": "High vitamin K can reduce warfarin effectiveness.", "recommendation": "Keep vitamin K intake consistent."}
             ]},
            {"food_name": "Cranberry Juice", "had_interaction": True, "interaction_count": 1, "max_severity": "moderate", "hours_ago": 24,
             "medications": ["Warfarin"],
             "interactions": [
                 {"drugName": "Warfarin", "foodName": "Cranberry Juice", "severity": "moderate", "effect": "Cranberry may enhance warfarin's effect.", "recommendation": "Limit cranberry juice consumption."}
             ]},
            {"food_name": "Chicken Breast", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 48,
             "medications": ["Warfarin", "Aspirin"], "interactions": []},
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
            {"food_name": "Coffee", "had_interaction": True},
            {"food_name": "Fiber Cereal", "had_interaction": True},
        ],
        "food_diary": [
            {"food_name": "Oatmeal", "meal_type": "breakfast", "servings": 1, "calories": 150, "protein": 5, "carbs": 27, "fat": 3, "days_ago": 0},
            {"food_name": "Blueberries", "meal_type": "breakfast", "servings": 1, "calories": 85, "protein": 1, "carbs": 21, "fat": 0, "days_ago": 0},
            {"food_name": "Herbal Tea", "meal_type": "breakfast", "servings": 1, "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "days_ago": 0},
            {"food_name": "Tuna Salad", "meal_type": "lunch", "servings": 1, "calories": 280, "protein": 24, "carbs": 8, "fat": 18, "days_ago": 0},
            {"food_name": "Whole Grain Crackers", "meal_type": "lunch", "servings": 1, "calories": 120, "protein": 3, "carbs": 22, "fat": 3, "days_ago": 0},
            {"food_name": "Cottage Cheese", "meal_type": "snack", "servings": 1, "calories": 110, "protein": 14, "carbs": 4, "fat": 4, "days_ago": 0},
            {"food_name": "Peaches", "meal_type": "snack", "servings": 1, "calories": 60, "protein": 1, "carbs": 15, "fat": 0, "days_ago": 0},
            {"food_name": "Baked Cod", "meal_type": "dinner", "servings": 1, "calories": 190, "protein": 32, "carbs": 0, "fat": 6, "days_ago": 0},
            {"food_name": "Asparagus", "meal_type": "dinner", "servings": 1, "calories": 40, "protein": 4, "carbs": 8, "fat": 0, "days_ago": 0},
            {"food_name": "Wild Rice", "meal_type": "dinner", "servings": 1, "calories": 165, "protein": 7, "carbs": 35, "fat": 1, "days_ago": 0},
        ],
        "interaction_checks": [
            {"food_name": "Soy Milk", "had_interaction": True, "interaction_count": 2, "max_severity": "moderate", "hours_ago": 4,
             "medications": ["Synthroid", "Calcium"],
             "interactions": [
                 {"drugName": "Synthroid", "foodName": "Soy Milk", "severity": "moderate", "effect": "Soy can interfere with levothyroxine absorption.", "recommendation": "Take medication 4 hours apart from soy products."},
                 {"drugName": "Calcium", "foodName": "Soy Milk", "severity": "low", "effect": "Soy may slightly affect calcium absorption.", "recommendation": "Take at different times."}
             ]},
            {"food_name": "Coffee", "had_interaction": True, "interaction_count": 1, "max_severity": "moderate", "hours_ago": 28,
             "medications": ["Synthroid"],
             "interactions": [
                 {"drugName": "Synthroid", "foodName": "Coffee", "severity": "moderate", "effect": "Coffee reduces levothyroxine absorption.", "recommendation": "Wait 30-60 minutes after medication before coffee."}
             ]},
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
            {"drug_name": "Omeprazole", "brand_name": "Prilosec", "generic_name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "notes": "Stomach protection"},
        ],
        "searches": [
            {"food_name": "Milk", "had_interaction": True},
            {"food_name": "Cheese", "had_interaction": True},
            {"food_name": "Salmon", "had_interaction": False},
            {"food_name": "Yogurt", "had_interaction": True},
            {"food_name": "Antacids", "had_interaction": True},
        ],
        "food_diary": [
            {"food_name": "Fried Rice", "meal_type": "breakfast", "servings": 1, "calories": 320, "protein": 8, "carbs": 52, "fat": 10, "days_ago": 0},
            {"food_name": "Green Tea", "meal_type": "breakfast", "servings": 1, "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "days_ago": 0},
            {"food_name": "Beef Noodle Soup", "meal_type": "lunch", "servings": 1, "calories": 380, "protein": 28, "carbs": 42, "fat": 12, "days_ago": 0},
            {"food_name": "Spring Rolls", "meal_type": "lunch", "servings": 2, "calories": 200, "protein": 6, "carbs": 28, "fat": 8, "days_ago": 0},
            {"food_name": "Edamame", "meal_type": "snack", "servings": 1, "calories": 120, "protein": 11, "carbs": 9, "fat": 5, "days_ago": 0},
            {"food_name": "Kung Pao Chicken", "meal_type": "dinner", "servings": 1, "calories": 420, "protein": 32, "carbs": 18, "fat": 26, "days_ago": 0},
            {"food_name": "Steamed Rice", "meal_type": "dinner", "servings": 1, "calories": 200, "protein": 4, "carbs": 45, "fat": 0, "days_ago": 0},
            {"food_name": "Stir-Fried Vegetables", "meal_type": "dinner", "servings": 1, "calories": 95, "protein": 4, "carbs": 12, "fat": 4, "days_ago": 0},
        ],
        "interaction_checks": [
            {"food_name": "Milk", "had_interaction": True, "interaction_count": 1, "max_severity": "high", "hours_ago": 3,
             "medications": ["Ciprofloxacin"],
             "interactions": [
                 {"drugName": "Ciprofloxacin", "foodName": "Milk", "severity": "high", "effect": "Dairy significantly reduces ciprofloxacin absorption.", "recommendation": "Avoid dairy 2 hours before and 6 hours after taking medication."}
             ]},
            {"food_name": "Cheese", "had_interaction": True, "interaction_count": 1, "max_severity": "high", "hours_ago": 18,
             "medications": ["Ciprofloxacin"],
             "interactions": [
                 {"drugName": "Ciprofloxacin", "foodName": "Cheese", "severity": "high", "effect": "Calcium in cheese binds to ciprofloxacin.", "recommendation": "Avoid dairy products near medication times."}
             ]},
            {"food_name": "Salmon", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 42,
             "medications": ["Ciprofloxacin", "Ibuprofen"], "interactions": []},
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
            {"drug_name": "Vitamin B12", "brand_name": "Nature Made", "generic_name": "Cyanocobalamin", "dosage": "1000mcg", "frequency": "Once daily", "notes": "Energy supplement"},
        ],
        "searches": [
            {"food_name": "Alcohol", "had_interaction": True},
            {"food_name": "Grapefruit Juice", "had_interaction": True},
            {"food_name": "Pasta", "had_interaction": False},
            {"food_name": "Avocado", "had_interaction": False},
            {"food_name": "St. John's Wort Tea", "had_interaction": True},
            {"food_name": "Tryptophan Foods", "had_interaction": True},
        ],
        "food_diary": [
            {"food_name": "Avocado Toast", "meal_type": "breakfast", "servings": 1, "calories": 280, "protein": 7, "carbs": 25, "fat": 18, "days_ago": 0},
            {"food_name": "Latte", "meal_type": "breakfast", "servings": 1, "calories": 150, "protein": 8, "carbs": 15, "fat": 6, "days_ago": 0},
            {"food_name": "Acai Bowl", "meal_type": "lunch", "servings": 1, "calories": 380, "protein": 5, "carbs": 72, "fat": 10, "days_ago": 0},
            {"food_name": "Protein Smoothie", "meal_type": "snack", "servings": 1, "calories": 220, "protein": 25, "carbs": 18, "fat": 5, "days_ago": 0},
            {"food_name": "Poke Bowl", "meal_type": "dinner", "servings": 1, "calories": 520, "protein": 32, "carbs": 58, "fat": 18, "days_ago": 0},
            {"food_name": "Miso Soup", "meal_type": "dinner", "servings": 1, "calories": 40, "protein": 3, "carbs": 5, "fat": 1, "days_ago": 0},
        ],
        "interaction_checks": [
            {"food_name": "Alcohol", "had_interaction": True, "interaction_count": 2, "max_severity": "high", "hours_ago": 8,
             "medications": ["Prozac", "Xanax"],
             "interactions": [
                 {"drugName": "Prozac", "foodName": "Alcohol", "severity": "high", "effect": "Alcohol can worsen depression and increase side effects.", "recommendation": "Avoid alcohol while taking antidepressants."},
                 {"drugName": "Xanax", "foodName": "Alcohol", "severity": "high", "effect": "Combining can cause dangerous sedation and respiratory depression.", "recommendation": "Never mix with alcohol."}
             ]},
            {"food_name": "Grapefruit Juice", "had_interaction": True, "interaction_count": 1, "max_severity": "moderate", "hours_ago": 32,
             "medications": ["Xanax"],
             "interactions": [
                 {"drugName": "Xanax", "foodName": "Grapefruit Juice", "severity": "moderate", "effect": "Grapefruit can increase alprazolam levels.", "recommendation": "Avoid grapefruit products."}
             ]},
            {"food_name": "Pasta", "had_interaction": False, "interaction_count": 0, "max_severity": None, "hours_ago": 56,
             "medications": ["Prozac", "Birth Control"], "interactions": []},
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
        food_logs_created = 0
        interaction_checks_created = 0
        
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
                search_time = datetime.now(timezone.utc) - timedelta(hours=i * 3, minutes=i * 10)
                
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
            
            # Add food diary entries
            food_diary_entries = user_data.get("food_diary", [])
            today = date.today()
            for food_data in food_diary_entries:
                days_ago = food_data.get("days_ago", 0)
                log_date = today - timedelta(days=days_ago)
                
                food_log = FoodLog(
                    user_id=user.id,
                    food_name=food_data["food_name"],
                    meal_type=food_data.get("meal_type", "snack"),
                    servings=food_data.get("servings", 1),
                    calories=food_data.get("calories"),
                    protein=food_data.get("protein"),
                    carbs=food_data.get("carbs"),
                    fat=food_data.get("fat"),
                    logged_date=log_date
                )
                db.session.add(food_log)
                food_logs_created += 1
            
            if food_diary_entries:
                print(f"   🍎 Added {len(food_diary_entries)} food diary entries")
            
            # Add interaction check history
            interaction_checks = user_data.get("interaction_checks", [])
            for check_data in interaction_checks:
                hours_ago = check_data.get("hours_ago", 0)
                check_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
                
                check = InteractionCheck(
                    user_id=user.id,
                    food_name=check_data["food_name"],
                    medications_checked=json.dumps(check_data.get("medications", [])),
                    had_interaction=check_data["had_interaction"],
                    interaction_count=check_data.get("interaction_count", 0),
                    interactions_json=json.dumps(check_data.get("interactions", [])) if check_data.get("interactions") else None,
                    max_severity=check_data.get("max_severity"),
                    checked_at=check_time
                )
                db.session.add(check)
                interaction_checks_created += 1
            
            if interaction_checks:
                print(f"   ⚠️  Added {len(interaction_checks)} interaction check history items")
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "=" * 50)
        print(f"🎉 Seeding complete!")
        print(f"   👤 Users created: {users_created}")
        print(f"   💊 Medications created: {medications_created}")
        print(f"   🔍 Search history items: {searches_created}")
        print(f"   🍎 Food diary entries: {food_logs_created}")
        print(f"   ⚠️  Interaction checks: {interaction_checks_created}")
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
        # Ensure all tables exist first
        db.create_all()
        
        print("\n⚠️  Clearing all data...")
        
        # Delete in order to respect foreign keys
        InteractionCheck.query.delete()
        FoodLog.query.delete()
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
