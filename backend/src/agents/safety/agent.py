"""
Safety Agent
"""
from typing import List
from ..models import SafetyWarning, SafetyStatus, RiskLevel, QueryUnderstanding, RankedResult

class SafetyAgent:
    def __init__(self):
        self.high_risk_compounds = ["trenbolone", "superdrol", "halotestin", "anadrol"]
        self.extreme_risk_compounds = ["growth hormone", "insulin"]
        self.dangerous_keywords = ["suicide", "overdose", "death", "lethal", "fatal"]

    def process(self, query: QueryUnderstanding, results: List[RankedResult]) -> SafetyWarning:
        compound = query.compound or ""
        risk_level = query.risk_level
        
        warnings = []
        precautions = []
        status = SafetyStatus.SAFE
        
        # Check for dangerous compounds
        for name in self.high_risk_compounds:
            if name in compound.lower():
                warnings.append(f"{name} is a high-risk compound with significant side effects.")
                status = SafetyStatus.WARNING
        
        for name in self.extreme_risk_compounds:
            if name in compound.lower():
                warnings.append(f"{name} requires extreme caution and medical supervision.")
                status = SafetyStatus.DANGER
        
        # Risk-based warnings
        if risk_level == RiskLevel.HIGH:
            warnings.append("This compound has a high risk profile. Medical supervision recommended.")
            status = SafetyStatus.WARNING
        elif risk_level == RiskLevel.EXTREME:
            warnings.append("This compound has extreme risks. Do not use without medical supervision.")
            status = SafetyStatus.DANGER
        elif risk_level == RiskLevel.MODERATE:
            warnings.append("This compound has moderate risks. Research thoroughly before use.")
            if status == SafetyStatus.SAFE:
                status = SafetyStatus.CAUTION
        
        # General precautions
        precautions = [
            "Always consult a healthcare professional before use.",
            "Start with the lowest effective dose.",
            "Monitor for adverse effects regularly.",
            "Consider blood work before and during use.",
            "Never share prescriptions or use without guidance."
        ]
        
        disclaimer = "This information is for educational purposes only. Always consult a qualified healthcare provider before starting any supplement, peptide, or anabolic compound regimen."
        
        return SafetyWarning(
            status=status,
            level=risk_level,
            warnings=warnings,
            precautions=precautions,
            disclaimer=disclaimer
        )


agent = SafetyAgent()

def analyze_safety(query: QueryUnderstanding, results: List[RankedResult]) -> SafetyWarning:
    return agent.process(query, results)
