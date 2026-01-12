"""
OpenFDA API Service
Handles all drug-related API calls to FDA database
Docs: https://open.fda.gov/apis/drug/
"""

import requests

BASE_URL = "https://api.fda.gov/drug"


def search_drug(query: str, limit: int = 5):
    """
    Search drugs by brand or generic name
    Returns: list of drug results with label info
    """
    url = f"{BASE_URL}/label.json"
    params = {
        "search": f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Parse and clean up results
            drugs = []
            for item in results:
                openfda = item.get("openfda", {})
                drug = {
                    "brand_name": openfda.get("brand_name", ["Unknown"])[0],
                    "generic_name": openfda.get("generic_name", ["Unknown"])[0],
                    "manufacturer": openfda.get("manufacturer_name", ["Unknown"])[0],
                    "purpose": item.get("purpose", ["Not specified"])[0] if item.get("purpose") else "Not specified",
                    "warnings": item.get("warnings", ["No warnings listed"])[0] if item.get("warnings") else "No warnings listed",
                    "dosage": item.get("dosage_and_administration", ["See label"])[0] if item.get("dosage_and_administration") else "See label",
                    "active_ingredient": item.get("active_ingredient", ["Not listed"])[0] if item.get("active_ingredient") else "Not listed",
                }
                drugs.append(drug)
            
            return {"success": True, "count": len(drugs), "drugs": drugs}
        
        elif response.status_code == 404:
            return {"success": True, "count": 0, "drugs": [], "message": "No drugs found"}
        
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_adverse_events(drug_name: str, limit: int = 5):
    """
    Get adverse event reports for a drug
    Returns: list of reported adverse events
    """
    url = f"{BASE_URL}/event.json"
    params = {
        "search": f'patient.drug.openfda.brand_name:"{drug_name}"',
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            events = []
            for item in results:
                reactions = item.get("patient", {}).get("reaction", [])
                reaction_list = [r.get("reactionmeddrapt", "Unknown") for r in reactions]
                
                event = {
                    "serious": item.get("serious", 0) == 1,
                    "reactions": reaction_list[:5],  # Top 5 reactions
                    "outcome": item.get("patient", {}).get("patientonsetage", "Unknown"),
                }
                events.append(event)
            
            return {"success": True, "count": len(events), "events": events}
        
        elif response.status_code == 404:
            return {"success": True, "count": 0, "events": [], "message": "No adverse events found"}
        
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_drug_recalls(drug_name: str, limit: int = 5):
    """
    Check for drug recalls
    Returns: list of recall information
    """
    url = f"{BASE_URL}/enforcement.json"
    params = {
        "search": f'product_description:"{drug_name}"',
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            recalls = []
            for item in results:
                recall = {
                    "reason": item.get("reason_for_recall", "Not specified"),
                    "classification": item.get("classification", "Unknown"),
                    "status": item.get("status", "Unknown"),
                    "recall_date": item.get("recall_initiation_date", "Unknown"),
                }
                recalls.append(recall)
            
            return {"success": True, "count": len(recalls), "recalls": recalls}
        
        elif response.status_code == 404:
            return {"success": True, "count": 0, "recalls": [], "message": "No recalls found"}
        
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}