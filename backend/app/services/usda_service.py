"""
USDA FoodData Central API Service
Handles all food/nutrition-related API calls
Docs: https://fdc.nal.usda.gov/api-guide/
"""

import os
import requests
from flask import current_app

BASE_URL = "https://api.nal.usda.gov/fdc/v1"


def get_api_key():
    """Get API key from config or environment"""
    try:
        return current_app.config.get('USDA_API_KEY') or os.getenv('USDA_API_KEY', '')
    except RuntimeError:
        return os.getenv('USDA_API_KEY', '')


def search_food(query: str, limit: int = 10, data_type: list = None):
    """
    Search foods by name
    data_type options: Branded, Foundation, SR Legacy, Survey (FNDDS)
    """
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "USDA API key not configured"}
    
    url = f"{BASE_URL}/foods/search"
    params = {
        "api_key": api_key,
        "query": query,
        "pageSize": limit,
    }
    
    if data_type:
        params["dataType"] = data_type
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            foods_raw = data.get("foods", [])
            
            foods = []
            for item in foods_raw:
                nutrients = {n.get("nutrientName"): n.get("value") for n in item.get("foodNutrients", [])}
                
                food = {
                    "fdc_id": item.get("fdcId"),
                    "description": item.get("description", "Unknown"),
                    "brand_owner": item.get("brandOwner", "Generic"),
                    "data_type": item.get("dataType", "Unknown"),
                    "serving_size": item.get("servingSize"),
                    "serving_unit": item.get("servingSizeUnit", "g"),
                    "nutrients": {
                        "calories": nutrients.get("Energy", 0),
                        "protein": nutrients.get("Protein", 0),
                        "fat": nutrients.get("Total lipid (fat)", 0),
                        "carbs": nutrients.get("Carbohydrate, by difference", 0),
                        "fiber": nutrients.get("Fiber, total dietary", 0),
                        "sugar": nutrients.get("Sugars, total including NLEA", nutrients.get("Total Sugars", 0)),
                        "sodium": nutrients.get("Sodium, Na", 0),
                    }
                }
                foods.append(food)
            
            return {
                "success": True,
                "count": len(foods),
                "total_hits": data.get("totalHits", 0),
                "foods": foods
            }
        
        elif response.status_code == 404:
            return {"success": True, "count": 0, "foods": [], "message": "No foods found"}
        
        elif response.status_code == 403:
            return {"success": False, "error": "Invalid API key"}
        
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_food_details(fdc_id: int):
    """
    Get detailed nutrition info for a specific food
    """
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "USDA API key not configured"}
    
    url = f"{BASE_URL}/food/{fdc_id}"
    params = {"api_key": api_key}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            item = response.json()
            
            nutrients_raw = item.get("foodNutrients", [])
            nutrients = {}
            for n in nutrients_raw:
                name = n.get("nutrient", {}).get("name") or n.get("nutrientName")
                value = n.get("amount") or n.get("value", 0)
                unit = n.get("nutrient", {}).get("unitName") or n.get("unitName", "")
                if name:
                    nutrients[name] = {"value": value, "unit": unit}
            
            food = {
                "fdc_id": item.get("fdcId"),
                "description": item.get("description", "Unknown"),
                "brand_owner": item.get("brandOwner", "Generic"),
                "data_type": item.get("dataType", "Unknown"),
                "serving_size": item.get("servingSize"),
                "serving_unit": item.get("servingSizeUnit", "g"),
                "ingredients": item.get("ingredients", ""),
                "nutrients": {
                    "calories": nutrients.get("Energy", {}).get("value", 0),
                    "protein": nutrients.get("Protein", {}).get("value", 0),
                    "fat": nutrients.get("Total lipid (fat)", {}).get("value", 0),
                    "carbs": nutrients.get("Carbohydrate, by difference", {}).get("value", 0),
                    "fiber": nutrients.get("Fiber, total dietary", {}).get("value", 0),
                    "sugar": nutrients.get("Sugars, total including NLEA", nutrients.get("Total Sugars", {})).get("value", 0),
                    "sodium": nutrients.get("Sodium, Na", {}).get("value", 0),
                    "cholesterol": nutrients.get("Cholesterol", {}).get("value", 0),
                    "saturated_fat": nutrients.get("Fatty acids, total saturated", {}).get("value", 0),
                    "vitamin_c": nutrients.get("Vitamin C, total ascorbic acid", {}).get("value", 0),
                    "calcium": nutrients.get("Calcium, Ca", {}).get("value", 0),
                    "iron": nutrients.get("Iron, Fe", {}).get("value", 0),
                    "potassium": nutrients.get("Potassium, K", {}).get("value", 0),
                },
                "all_nutrients": nutrients
            }
            
            return {"success": True, "food": food}
        
        elif response.status_code == 404:
            return {"success": False, "error": "Food not found"}
        
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}