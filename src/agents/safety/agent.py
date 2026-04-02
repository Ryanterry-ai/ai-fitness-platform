"""Safety Agent"""
from typing import List
from ..models import SafetyWarning, SafetyStatus, RiskLevel, QueryUnderstanding, RankedResult

class SafetyAgent:
    def __init__(self):
        self.extreme = ["trenbolone", "superdrol", "halotestin", "anadrol"]
        self.high = ["testosterone", "nandrolone", "hgh", "dianabol"]

    def process(self, query: QueryUnderstanding, results: List[RankedResult]) -> SafetyWarning:
        compound = query.compound or ""
        risk = query.risk_level
        warnings, status = [], SafetyStatus.SAFE
        
        for name in self.extreme:
            if name in compound.lower():
                warnings.append(f"{name} has extreme risks. Medical supervision required.")
                status = SafetyStatus.DANGER
        for name in self.high:
            if name in compound.lower():
                warnings.append(f"{name} requires careful monitoring and proper PCT.")
                if status == SafetyStatus.SAFE:
                    status = SafetyStatus.WARNING
        
        if risk == RiskLevel.HIGH:
            warnings.append("High-risk compound. Medical supervision recommended.")
            status = SafetyStatus.WARNING
        elif risk == RiskLevel.EXTREME:
            warnings.append("Extreme risk. Do not use without medical supervision.")
            status = SafetyStatus.DANGER
        elif risk == RiskLevel.MODERATE:
            warnings.append("Moderate risk. Research thoroughly before use.")
            if status == SafetyStatus.SAFE:
                status = SafetyStatus.CAUTION
        
        return SafetyWarning(
            status=status, level=risk, warnings=warnings,
            precautions=["Consult healthcare professional", "Start with lowest dose", "Monitor blood work", "Never share prescriptions"],
            disclaimer="This information is for educational purposes only. Always consult a qualified healthcare provider."
        )

agent = SafetyAgent()

def analyze_safety(query: QueryUnderstanding, results: List[RankedResult]) -> SafetyWarning:
    return agent.process(query, results)
