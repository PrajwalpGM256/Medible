"""
Food-Drug Interaction Service
Core business logic for checking interactions between foods and medications
"""

import json
import os
import re
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class InteractionResult:
    """Represents a single interaction match"""
    interaction_id: str
    food_name: str
    drug_name: str
    drug_class: str
    severity: str
    effect: str
    recommendation: str
    evidence_level: str
    matched_food_term: str
    matched_drug_term: str


class InteractionEngine:
    """
    Singleton-style interaction checker engine
    Loads interaction data once and provides efficient lookups
    """
    
    _instance = None
    _interactions = None

    # Commonly used synonyms for better matching
    _synonyms = {
        "grape juice": "grapefruit",
        "dairy": "milk",
        "peanut butter": "peanut",
        "gluten": "wheat"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_interactions()
        return cls._instance
    
    def _load_interactions(self):
        """Load interaction data from JSON file"""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'food_drug_interactions.json'
        )
        
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                self._interactions = data.get('interactions', [])
                self._version = data.get('version', 'unknown')
                self._last_updated = data.get('last_updated', 'unknown')
        except FileNotFoundError:
            self._interactions = []
            self._version = 'unknown'
            self._last_updated = 'unknown'
        except json.JSONDecodeError:
            self._interactions = []
            self._version = 'error'
            self._last_updated = 'error'
    
    def reload(self):
        """Force reload of interaction data (useful for updates)"""
        self._load_interactions()
    
    @property
    def stats(self) -> dict:
        """Get statistics about loaded interactions"""
        if not self._interactions:
            return {"count": 0, "version": self._version, "last_updated": self._last_updated}
        
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        drug_classes = set()
        food_categories = set()
        
        for interaction in self._interactions:
            severity_counts[interaction.get('severity', 'low')] += 1
            drug_classes.add(interaction.get('drug', {}).get('class', 'unknown'))
            food_categories.add(interaction.get('food', {}).get('category', 'unknown'))
        
        return {
            "total_interactions": len(self._interactions),
            "version": self._version,
            "last_updated": self._last_updated,
            "severity_breakdown": severity_counts,
            "drug_classes": len(drug_classes),
            "food_categories": len(food_categories)
        }
    
    def _normalize(self, text) -> str:
        """Normalize text for matching (lowercase, remove special chars, apply synonyms)"""
        if not text:
            return ""
        
        # If the input is a list (e.g. from OpenFDA), join it into a string
        if isinstance(text, list):
            text = " ".join(str(item) for item in text)
            
        normalized = re.sub(r'[^a-z0-9\s]', '', str(text).lower().strip())
        
        # Apply synonyms
        for k, v in self._synonyms.items():
            if k in normalized:
                normalized = normalized.replace(k, v)
                break
                
        return normalized
    
    def _fuzzy_match(self, query: str, targets: list) -> Optional[str]:
        """
        Check if query matches any target (exact or partial)
        Returns the matched term or None
        """
        query_normalized = self._normalize(query)
        
        for target in targets:
            target_normalized = self._normalize(target)
            
            # Exact match
            if query_normalized == target_normalized:
                return target
            
            # Query contains target or target contains query
            if query_normalized in target_normalized or target_normalized in query_normalized:
                return target
            
            # Word-level matching for multi-word terms
            query_words = set(query_normalized.split())
            target_words = set(target_normalized.split())
            
            # If all query words are in target (or vice versa for short queries)
            if query_words and target_words:
                if query_words.issubset(target_words) or target_words.issubset(query_words):
                    return target
        
        return None
    
    def _match_food(self, food_query: str, food_data: dict) -> Optional[str]:
        """Check if food query matches this interaction's food"""
        food_name = food_data.get('name', '')
        aliases = food_data.get('aliases', [])
        
        all_terms = [food_name] + aliases
        return self._fuzzy_match(food_query, all_terms)
    
    def _match_drug(self, drug_query: str, drug_data: dict) -> Optional[str]:
        """Check if drug query matches this interaction's drug"""
        generic_names = drug_data.get('names', [])
        brand_names = drug_data.get('brand_names', [])
        drug_class = drug_data.get('class', '')
        
        all_terms = generic_names + brand_names + [drug_class]
        return self._fuzzy_match(drug_query, all_terms)
    
    def check_interaction(self, food: str, drug: str) -> List[InteractionResult]:
        """
        Check for interactions between a food and a drug
        Returns list of matching interactions (can be multiple)
        """
        if not food or not drug:
            return []
        
        results = []
        
        for interaction in self._interactions:
            food_data = interaction.get('food', {})
            drug_data = interaction.get('drug', {})
            
            food_match = self._match_food(food, food_data)
            drug_match = self._match_drug(drug, drug_data)
            
            if food_match and drug_match:
                results.append(InteractionResult(
                    interaction_id=interaction.get('id', 'unknown'),
                    food_name=food_data.get('name', 'Unknown'),
                    drug_name=drug_data.get('names', ['Unknown'])[0],
                    drug_class=drug_data.get('class', 'unknown'),
                    severity=interaction.get('severity', 'unknown'),
                    effect=interaction.get('effect', ''),
                    recommendation=interaction.get('recommendation', ''),
                    evidence_level=interaction.get('evidence_level', 'unknown'),
                    matched_food_term=food_match,
                    matched_drug_term=drug_match
                ))
        
        # If no local JSON matches, check OpenFDA dynamically for allergies & text warnings
        if not results:
            from app.services.openfda_service import get_drug_detail
            fda_res = get_drug_detail(drug)
            
            if fda_res.get('success') and fda_res.get('drug'):
                drug_info = fda_res['drug']
                norm_food = self._normalize(food)
                found_allergy = False
                
                # Check ingredients (allergies)
                act_ing = self._normalize(drug_info.get('active_ingredient', ''))
                inact_ing = self._normalize(drug_info.get('inactive_ingredient', ''))
                
                if norm_food in act_ing or norm_food in inact_ing:
                    results.append(InteractionResult(
                        interaction_id=f"FDA-ALG-{drug.upper()}",
                        food_name=food,
                        drug_name=drug_info.get('brand_name', drug),
                        drug_class='FDA Dynamic Check',
                        severity='high',
                        effect=f"Contains {food} as an ingredient. Potential for severe allergic reaction.",
                        recommendation="Avoid this medication and consult your prescriber immediately.",
                        evidence_level="strong",
                        matched_food_term=food,
                        matched_drug_term=drug
                    ))
                    found_allergy = True
                
                # Check interaction texts
                if not found_allergy:
                    inter_txt = self._normalize(drug_info.get('drug_interactions', ''))
                    warn_txt = self._normalize(drug_info.get('warnings', ''))
                    contra_txt = self._normalize(drug_info.get('contraindications', ''))
                    
                    if norm_food in inter_txt or norm_food in warn_txt or norm_food in contra_txt:
                        results.append(InteractionResult(
                            interaction_id=f"FDA-TXT-{drug.upper()}",
                            food_name=food,
                            drug_name=drug_info.get('brand_name', drug),
                            drug_class='FDA Dynamic Check',
                            severity='medium',
                            effect=f"The FDA label for this drug mentions '{food}' in its warnings or interactions.",
                            recommendation="Review the FDA drug label or consult a pharmacist to evaluate safely consuming this item.",
                            evidence_level="moderate",
                            matched_food_term=food,
                            matched_drug_term=drug
                        ))

        # Sort by severity (high first)
        severity_order = {'high': 0, 'medium': 1, 'low': 2, 'unknown': 3}
        results.sort(key=lambda x: severity_order.get(x.severity, 3))
        
        return results
    
    def check_food_against_medications(self, food: str, medications: List[str]) -> dict:
        """
        Check a single food against multiple medications
        Returns aggregated results grouped by severity
        """
        all_results = []
        medications_checked = []
        
        for med in medications:
            med = med.strip()
            if not med:
                continue
                
            medications_checked.append(med)
            results = self.check_interaction(food, med)
            all_results.extend(results)
        
        # Group by severity
        grouped = {"high": [], "medium": [], "low": []}
        seen_ids = set()  # Avoid duplicates
        
        for result in all_results:
            if result.interaction_id not in seen_ids:
                seen_ids.add(result.interaction_id)
                severity = result.severity if result.severity in grouped else "low"
                grouped[severity].append({
                    "interaction_id": result.interaction_id,
                    "food": result.food_name,
                    "drug": result.drug_name,
                    "drug_class": result.drug_class,
                    "effect": result.effect,
                    "recommendation": result.recommendation,
                    "evidence_level": result.evidence_level
                })
        
        return {
            "food_checked": food,
            "medications_checked": medications_checked,
            "total_warnings": len(seen_ids),
            "has_high_severity": len(grouped["high"]) > 0,
            "warnings": grouped
        }
    
    def get_all_interactions_for_drug(self, drug: str) -> List[dict]:
        """Get all known food interactions for a specific drug"""
        results = []
        
        for interaction in self._interactions:
            drug_data = interaction.get('drug', {})
            
            if self._match_drug(drug, drug_data):
                food_data = interaction.get('food', {})
                results.append({
                    "interaction_id": interaction.get('id'),
                    "food": food_data.get('name'),
                    "food_category": food_data.get('category'),
                    "foods_to_avoid": [food_data.get('name')] + food_data.get('aliases', [])[:3],
                    "severity": interaction.get('severity'),
                    "effect": interaction.get('effect'),
                    "recommendation": interaction.get('recommendation')
                })
        
        return results
    
    def get_all_interactions_for_food(self, food: str) -> List[dict]:
        """Get all known drug interactions for a specific food"""
        results = []
        
        for interaction in self._interactions:
            food_data = interaction.get('food', {})
            
            if self._match_food(food, food_data):
                drug_data = interaction.get('drug', {})
                results.append({
                    "interaction_id": interaction.get('id'),
                    "drug_class": drug_data.get('class'),
                    "affected_drugs": drug_data.get('names', [])[:5],
                    "affected_brands": drug_data.get('brand_names', [])[:5],
                    "severity": interaction.get('severity'),
                    "effect": interaction.get('effect'),
                    "recommendation": interaction.get('recommendation')
                })
        
        return results


# Module-level singleton instance
_engine = None


def get_engine() -> InteractionEngine:
    """Get or create the interaction engine singleton"""
    global _engine
    if _engine is None:
        _engine = InteractionEngine()
    return _engine


def check_interaction(food: str, drug: str) -> List[InteractionResult]:
    """Convenience function to check a single food-drug pair"""
    return get_engine().check_interaction(food, drug)


def check_food_against_medications(food: str, medications: List[str]) -> dict:
    """Convenience function to check food against multiple meds"""
    return get_engine().check_food_against_medications(food, medications)


def get_drug_interactions(drug: str) -> List[dict]:
    """Get all food interactions for a drug"""
    return get_engine().get_all_interactions_for_drug(drug)


def get_food_interactions(food: str) -> List[dict]:
    """Get all drug interactions for a food"""
    return get_engine().get_all_interactions_for_food(food)


def get_interaction_stats() -> dict:
    """Get statistics about the interaction database"""
    return get_engine().stats