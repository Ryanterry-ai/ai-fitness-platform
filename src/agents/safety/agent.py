"""
Safety Agent
============
Analyzes queries and results for safety concerns.
"""

from typing import List, Dict, Any, Optional
from src.models import QueryUnderstanding, SafetyWarning, SafetyStatus, RiskLevel


class SafetyAgent:
    """
    Agent responsible for safety analysis and warnings.
    
    Responsibilities:
    - Detect dangerous compounds and dosages
    - Assess beginner risks
    - Add appropriate warnings and disclaimers
    - Provide safety recommendations
    """
    
    # Dangerous dosages by compound
    DANGEROUS_DOSAGES = {
        "testosterone": {
            "safe_max": 1000,  # mg/week
            "dangerous": 1500,
            "note": "Above 1000mg/week significantly increases cardiovascular and hormonal risks"
        },
        "trenbolone": {
            "safe_max": 300,
            "dangerous": 500,
            "note": "High trenbolone doses can cause severe psychological effects and cardiovascular strain"
        },
        "rad140": {
            "safe_max": 20,
            "dangerous": 30,
            "note": "High RAD-140 doses may cause liver stress"
        },
        "hgh": {
            "safe_max": 4,  # IU/day
            "dangerous": 8,
            "note": "High HGH doses can cause insulin resistance and organ growth"
        }
    }
    
    # High-risk compounds requiring warnings
    HIGH_RISK_COMPOUNDS = [
        "trenbolone",
        "superdrol",
        "halotestin",
        "anadrol"
    ]
    
    # Age restrictions
    MIN_AGE_COMPOUNDS = {
        "steroids": 21,
        "sarms": 18,
        "peptides": 18,
        "hgh": 21
    }
    
    def __init__(self):
        self.always_disclaimer = (
            "This information is for educational purposes only. "
            "Always consult a qualified healthcare professional before starting any supplement, "
            "hormone, or performance-enhancing compound protocol."
        )
    
    def process(
        self,
        query_understanding: QueryUnderstanding,
        dosage_info: Optional[Dict[str, Any]] = None
    ) -> SafetyWarning:
        """
        Analyze query and content for safety concerns.
        
        Args:
            query_understanding: Parsed query understanding
            dosage_info: Optional extracted dosage information
            
        Returns:
            SafetyWarning object with warnings and recommendations
        """
        warnings = []
        recommendations = []
        disclaimers = []
        status = SafetyStatus.SAFE
        
        # Check for dangerous compounds
        compound_warnings = self._check_dangerous_compounds(query_understanding)
        warnings.extend(compound_warnings)
        
        # Check for dangerous dosages
        if dosage_info:
            dosage_warnings = self._check_dangerous_dosages(dosage_info)
            warnings.extend(dosage_warnings)
        
        # Check for beginner risks
        beginner_warnings = self._check_beginner_risks(query_understanding)
        warnings.extend(beginner_warnings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(query_understanding)
        
        # Add disclaimers
        disclaimers = self._generate_disclaimers(query_understanding)
        
        # Determine overall status
        if any("dangerous" in w.lower() or "extreme" in w.lower() for w in warnings):
            status = SafetyStatus.DANGER
        elif warnings or disclaimers:
            status = SafetyStatus.WARNING if len(warnings) > 2 else SafetyStatus.CAUTION
        else:
            status = SafetyStatus.SAFE
        
        # Determine severity
        severity = "high" if status == SafetyStatus.DANGER else (
            "moderate" if status == SafetyStatus.WARNING else "low"
        )
        
        return SafetyWarning(
            status=status,
            warnings=warnings,
            recommendations=recommendations,
            disclaimers=disclaimers,
            severity=severity
        )
    
    def _check_dangerous_compounds(
        self,
        query_understanding: QueryUnderstanding
    ) -> List[str]:
        """Check for dangerous compound queries"""
        warnings = []
        
        compound = query_understanding.compound
        if compound:
            compound_lower = compound.lower().replace("-", "")
            
            # Check for high-risk compounds
            for high_risk in self.HIGH_RISK_COMPOUNDS:
                if high_risk in compound_lower:
                    warnings.append(
                        f"{compound} is considered extremely dangerous and is not recommended "
                        "for any use due to severe potential side effects."
                    )
        
        # Check risk level
        if query_understanding.risk_level == RiskLevel.EXTREME:
            warnings.append(
                "This query involves compounds with extreme risk profiles. "
                "Extreme caution is advised."
            )
        elif query_understanding.risk_level == RiskLevel.HIGH:
            warnings.append(
                "This query involves compounds with high risk profiles. "
                "Proper medical supervision is essential."
            )
        
        return warnings
    
    def _check_dangerous_dosages(
        self,
        dosage_info: Dict[str, Any]
    ) -> List[str]:
        """Check for dangerous dosage queries"""
        warnings = []
        
        compound = dosage_info.get("compound", "").lower().replace("-", "")
        dosage = dosage_info.get("dosage", 0)
        unit = dosage_info.get("unit", "mg")
        
        # Convert to standard unit
        if unit == "mg/week" and compound in self.DANGEROUS_DOSAGES:
            threshold = self.DANGEROUS_DOSAGES[compound]
            
            if dosage > threshold.get("dangerous", float("inf")):
                warnings.append(
                    f"DOSAGE WARNING: {dosage}{unit} of {compound} is considered dangerous. "
                    f"Maximum safe dosage is {threshold.get('safe_max', 'unknown')}{unit}. "
                    f"{threshold.get('note', '')}"
                )
            elif dosage > threshold.get("safe_max", float("inf")):
                warnings.append(
                    f"CAUTION: {dosage}{unit} exceeds typical safe maximum for {compound}. "
                    f"{threshold.get('note', '')}"
                )
        
        return warnings
    
    def _check_beginner_risks(
        self,
        query_understanding: QueryUnderstanding
    ) -> List[str]:
        """Check for beginner-specific risks"""
        warnings = []
        
        compound = query_understanding.compound
        
        # Check if compound is safe for beginners
        if compound and query_understanding.experience_level == "beginner":
            beginner_safe_compounds = [
                "creatine", "whey", "caffeine", "beta-alanine",
                "citrulline", "omega-3", "vitamin d"
            ]
            
            is_safe = any(safe in compound.lower() for safe in beginner_safe_compounds)
            
            if not is_safe and query_understanding.domain.value in ["steroids", "sarms", "hgh"]:
                warnings.append(
                    f"BEGINNER WARNING: {compound} is not recommended for beginners. "
                    "Start with foundational supplements and build experience before considering "
                    "advanced compounds."
                )
        
        return warnings
    
    def _generate_recommendations(
        self,
        query_understanding: QueryUnderstanding
    ) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        # General bloodwork recommendation
        if query_understanding.domain.value in ["steroids", "sarms", "hgh"]:
            recommendations.append(
                "Obtain baseline bloodwork before starting any cycle"
            )
            recommendations.append(
                "Monitor bloodwork throughout and after cycle"
            )
            recommendations.append(
                "Consult with a healthcare professional experienced in hormone therapy"
            )
        
        # Age-based recommendations
        if query_understanding.experience_level == "beginner":
            recommendations.append(
                "Focus on nutrition, training, and foundational supplements first"
            )
            recommendations.append(
                "Build consistency before considering advanced compounds"
            )
        
        # Compound-specific recommendations
        compound = query_understanding.compound
        if compound:
            if "testosterone" in compound.lower():
                recommendations.append(
                    "Use an aromatase inhibitor (AI) if estrogen symptoms occur"
                )
                recommendations.append(
                    "Always run a proper PCT protocol after cycle"
                )
            elif "bpc" in compound.lower() or "peptide" in compound.lower():
                recommendations.append(
                    "Source peptides from reputable vendors with third-party testing"
                )
                recommendations.append(
                    "Use sterile technique when injecting"
                )
        
        return recommendations
    
    def _generate_disclaimers(
        self,
        query_understanding: QueryUnderstanding
    ) -> List[str]:
        """Generate required disclaimers"""
        disclaimers = [self.always_disclaimer]
        
        # Domain-specific disclaimers
        if query_understanding.domain.value == "steroids":
            disclaimers.append(
                "Anabolic steroids are controlled substances in many countries and require a prescription."
            )
        elif query_understanding.domain.value == "sarms":
            disclaimers.append(
                "SARMs are research chemicals not approved for human consumption by the FDA."
            )
        elif query_understanding.domain.value == "hgh":
            disclaimers.append(
                "HGH is a prescription medication and should only be used under medical supervision."
            )
        
        # High-risk disclaimer
        if query_understanding.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]:
            disclaimers.append(
                "WARNING: This content involves high-risk substances. Use at your own risk "
                "and only with proper medical oversight."
            )
        
        return disclaimers


# Singleton instance
safety_agent = SafetyAgent()


def analyze_safety(
    query_understanding: QueryUnderstanding,
    dosage_info: Optional[Dict[str, Any]] = None
) -> SafetyWarning:
    """
    Convenience function for safety analysis.
    
    Args:
        query_understanding: Parsed query understanding
        dosage_info: Optional extracted dosage information
        
    Returns:
        SafetyWarning object
    """
    return safety_agent.process(query_understanding, dosage_info)
