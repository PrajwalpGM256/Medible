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


def get_drug_detail(drug_id: str):
    """
    Get full drug label by application number or search term
    Returns: detailed drug label information
    """
    url = f"{BASE_URL}/label.json"
    params = {
        "search": f'openfda.application_number:"{drug_id}" OR openfda.brand_name:"{drug_id}"',
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return {"success": True, "drug": None, "message": "Drug not found"}

            item = results[0]
            openfda = item.get("openfda", {})

            drug = {
                "brand_name": openfda.get("brand_name", ["Unknown"])[0],
                "generic_name": openfda.get("generic_name", ["Unknown"])[0],
                "manufacturer": openfda.get("manufacturer_name", ["Unknown"])[0],
                "application_number": openfda.get("application_number", [None])[0],
                "product_type": openfda.get("product_type", ["Unknown"])[0],
                "route": openfda.get("route", ["Unknown"])[0] if openfda.get("route") else "Unknown",
                "substance_name": openfda.get("substance_name", []),
                "purpose": item.get("purpose", ["Not specified"])[0] if item.get("purpose") else "Not specified",
                "indications_and_usage": item.get("indications_and_usage", ["Not specified"])[0] if item.get("indications_and_usage") else "Not specified",
                "warnings": item.get("warnings", ["No warnings listed"])[0] if item.get("warnings") else "No warnings listed",
                "dosage_and_administration": item.get("dosage_and_administration", ["See label"])[0] if item.get("dosage_and_administration") else "See label",
                "active_ingredient": item.get("active_ingredient", ["Not listed"])[0] if item.get("active_ingredient") else "Not listed",
                "inactive_ingredient": item.get("inactive_ingredient", ["Not listed"])[0] if item.get("inactive_ingredient") else "Not listed",
                "contraindications": item.get("contraindications", ["None listed"])[0] if item.get("contraindications") else "None listed",
                "drug_interactions": item.get("drug_interactions", ["None listed"])[0] if item.get("drug_interactions") else "None listed",
                "adverse_reactions": item.get("adverse_reactions", ["None listed"])[0] if item.get("adverse_reactions") else "None listed",
            }

            return {"success": True, "drug": drug}

        elif response.status_code == 404:
            return {"success": True, "drug": None, "message": "Drug not found"}

        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_drug_drug_interactions(drug_name: str):
    """
    Get drug-drug interaction info from the drug label
    Returns: interaction text from the label
    """
    url = f"{BASE_URL}/label.json"
    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return {"success": True, "interactions": None, "message": "Drug not found"}

            item = results[0]
            openfda = item.get("openfda", {})

            interactions_text = item.get("drug_interactions", ["None listed"])[0] if item.get("drug_interactions") else "None listed"

            return {
                "success": True,
                "drug": openfda.get("brand_name", ["Unknown"])[0],
                "generic_name": openfda.get("generic_name", ["Unknown"])[0],
                "interactions_text": interactions_text,
            }

        elif response.status_code == 404:
            return {"success": True, "interactions": None, "message": "No interaction data found"}

        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_side_effects(drug_name: str):
    """
    Get side effects / adverse reactions for a drug from FDA labels
    Returns: adverse reaction information from the label
    """
    url = f"{BASE_URL}/label.json"
    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                return {"success": True, "side_effects": None, "message": "Drug not found"}

            item = results[0]
            openfda = item.get("openfda", {})

            return {
                "success": True,
                "drug": openfda.get("brand_name", ["Unknown"])[0],
                "generic_name": openfda.get("generic_name", ["Unknown"])[0],
                "adverse_reactions": item.get("adverse_reactions", ["None listed"])[0] if item.get("adverse_reactions") else "None listed",
                "warnings": item.get("warnings", ["None listed"])[0] if item.get("warnings") else "None listed",
                "warnings_and_cautions": item.get("warnings_and_cautions", ["None listed"])[0] if item.get("warnings_and_cautions") else "None listed",
            }

        elif response.status_code == 404:
            return {"success": True, "side_effects": None, "message": "Drug not found"}

        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}