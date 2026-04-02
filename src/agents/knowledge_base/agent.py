"""
Knowledge Base Agent
Comprehensive knowledge base for fitness, bodybuilding, and performance compounds
"""
import re
from typing import List, Dict, Optional
from ..models import KnowledgeResult, DomainCategory, QueryUnderstanding

class KnowledgeBaseAgent:
    """
    Comprehensive Knowledge Base for SEO Query Universe
    Contains detailed information on all compounds, exercises, and topics
    """
    
    def __init__(self):
        self._build_compound_database()
        self._build_exercise_database()
        self._build_nutrition_database()
        self._build_supplement_database()
        self._build_protocol_database()
    
    def _build_compound_database(self):
        """Build comprehensive compound database"""
        self.compounds = {
            # ── SARMs ────────────────────────────────────────────────────────
            "RAD-140": {
                "name": "RAD-140 (Testolone)",
                "category": DomainCategory.SARMS,
                "description": "RAD-140 is a potent selective androgen receptor modulator (SARM) with high anabolic activity. It's one of the most powerful SARMs for building muscle mass and strength.",
                "full_description": """
RAD-140 (Testolone) is considered one of the most potent SARMs available. It was originally developed for treatment of muscle wasting conditions.

KEY CHARACTERISTICS:
• Anabolic Ratio: 90:1 (highly anabolic)
• Half-life: 16-20 hours
• Administration: Oral
• Detection Time: ~3 weeks

MECHANISM OF ACTION:
RAD-140 selectively binds to androgen receptors in muscle and bone tissue, promoting anabolic effects while minimizing androgenic side effects in other tissues.

CLINICAL RESEARCH:
• Phase I trials showed significant muscle mass increase
• Animal studies show 50-80% muscle mass gain
• Potential neuroprotective properties
                """,
                "dosage": {
                    "beginner": "10mg/day for 8 weeks",
                    "intermediate": "15mg/day for 10 weeks",
                    "advanced": "20-25mg/day for 12 weeks",
                    "male": "10-25mg/day",
                    "female": "5-10mg/day"
                },
                "timing": "Best taken in the morning with food. Half-life of 16-20 hours allows for once daily dosing.",
                "cycle": {
                    "length": "8-12 weeks",
                    "off_cycle": "4-6 weeks (minimum)",
                    "pct_required": True
                },
                "benefits": [
                    "Significant muscle mass gain",
                    "Increased strength",
                    "Improved bone density",
                    "Fat loss assistance",
                    "Enhanced recovery",
                    "Neuroprotective effects"
                ],
                "side_effects": [
                    "Testosterone suppression",
                    "Potential liver stress",
                    "Headaches",
                    "Aggression",
                    "Acne (occasional)"
                ],
                "stacks": [
                    {"compound": "LGD-4033", "purpose": "Maximum mass gain"},
                    {"compound": "MK-677", "purpose": "Enhanced recovery"},
                    {"compound": "Cardarine", "purpose": "Fat loss"}
                ],
                "pct": {
                    "recommended": "Nolvadex 20/10/10/10 or Clomid 25/25/12.5/12.5",
                    "duration": "4 weeks"
                },
                "safety": {
                    "risk_level": "moderate",
                    "suppression": "moderate to high",
                    "liver_toxicity": "low",
                    "cardiovascular": "minimal"
                },
                "research": [
                    {"title": "RAD140 for Muscle Wasting", "source": "PubMed", "year": 2010},
                    {"title": "SARM Development Studies", "source": "NCBI", "year": 2012}
                ],
                "evidence_tier": "high",
                "tags": ["sarms", "muscle gain", "strength", "mass", "bulking"],
                "related": ["LGD-4033", "Ostarine", "S-23"]
            },
            
            "LGD-4033": {
                "name": "LGD-4033 (Ligandrol)",
                "category": DomainCategory.SARMS,
                "description": "LGD-4033 is a potent SARM known for significant muscle building effects with excellent selectivity.",
                "full_description": """
LGD-4033 (Ligandrol) is one of the most researched SARMs with strong anabolic effects.

KEY CHARACTERISTICS:
• Anabolic Ratio: 50:1
• Half-life: 30-36 hours
• Administration: Oral
• Detection Time: ~4-5 weeks

MECHANISM OF ACTION:
Selectively activates androgen receptors in muscle and bone, promoting protein synthesis and nitrogen retention.
                """,
                "dosage": {
                    "beginner": "5mg/day for 8 weeks",
                    "intermediate": "10mg/day for 10 weeks",
                    "advanced": "10-15mg/day for 12 weeks",
                    "male": "5-15mg/day",
                    "female": "2.5-5mg/day"
                },
                "timing": "Once daily, can be taken with or without food. Long half-life allows flexible dosing.",
                "cycle": {
                    "length": "8-12 weeks",
                    "off_cycle": "6-8 weeks",
                    "pct_required": True
                },
                "benefits": [
                    "Rapid muscle mass gain",
                    "Increased strength",
                    "Improved recovery",
                    "Fat preservation",
                    "Joint healing"
                ],
                "side_effects": [
                    "Testosterone suppression",
                    "Headaches",
                    "Fatigue",
                    "Nausea (rare)"
                ],
                "stacks": [
                    {"compound": "RAD-140", "purpose": "Bulking stack"},
                    {"compound": "MK-677", "purpose": "Recomp stack"},
                    {"compound": "RAD-140 + Cardarine", "purpose": "Cutting stack"}
                ],
                "pct": {
                    "recommended": "Nolvadex 20/20/10/10 or Clomid 25/25/12.5/12.5",
                    "duration": "4 weeks"
                },
                "safety": {
                    "risk_level": "moderate",
                    "suppression": "moderate",
                    "liver_toxicity": "low",
                    "cardiovascular": "minimal"
                },
                "evidence_tier": "high",
                "tags": ["sarms", "muscle gain", "strength", "beginner-friendly"],
                "related": ["RAD-140", "Ostarine", "S-23"]
            },
            
            "Ostarine": {
                "name": "Ostarine (MK-2866)",
                "category": DomainCategory.SARMS,
                "description": "Ostarine is the most studied SARM with a mild profile, making it ideal for beginners.",
                "full_description": """
Ostarine (MK-2866) is the original SARM developed for treating muscle wasting. It has the most clinical research.

KEY CHARACTERISTICS:
• Anabolic Ratio: 10:1
• Half-life: 24 hours
• Administration: Oral
• Detection Time: ~2-3 weeks

BEST FOR: Beginners, body recomposition, and those seeking mild effects.
                """,
                "dosage": {
                    "beginner": "15mg/day for 8-12 weeks",
                    "intermediate": "20mg/day for 12 weeks",
                    "advanced": "25mg/day for 12 weeks",
                    "male": "15-25mg/day",
                    "female": "10-15mg/day"
                },
                "timing": "Once daily. Can be split into AM/PM doses for better absorption.",
                "cycle": {
                    "length": "8-12 weeks",
                    "off_cycle": "4 weeks",
                    "pct_required": "May not be required at lower doses"
                },
                "benefits": [
                    "Lean muscle preservation",
                    "Joint healing",
                    "Fat loss assistance",
                    "Mild anabolic effects",
                    "Excellent tolerability"
                ],
                "side_effects": [
                    "Mild testosterone suppression",
                    "Headaches (rare)",
                    "Back pumps (rare)"
                ],
                "stacks": [
                    {"compound": "S4", "purpose": "Cutting stack"},
                    {"compound": "LGD-4033", "purpose": "Bulk stack"},
                    {"compound": "MK-677", "purpose": "Recomp stack"}
                ],
                "safety": {
                    "risk_level": "low",
                    "suppression": "mild",
                    "liver_toxicity": "very low",
                    "cardiovascular": "none"
                },
                "evidence_tier": "very_high",
                "tags": ["sarms", "beginner", "cutting", "recomp", "mild"],
                "related": ["LGD-4033", "RAD-140", "S-22"]
            },
            
            "MK-677": {
                "name": "MK-677 (Ibutamoren)",
                "category": DomainCategory.SARMS,
                "description": "MK-677 is a growth hormone secretagogue that increases natural HGH and IGF-1 levels.",
                "full_description": """
MK-677 (Ibutamoren) is a potent growth hormone secretagogue that stimulates the pituitary gland to release more HGH.

KEY CHARACTERISTICS:
• Mechanism: Ghrelin receptor agonist
• Half-life: 4-6 hours
• Administration: Oral
• Effect: Increases HGH by 40-100%

MECHANISM OF ACTION:
Stimulates ghrelin receptors, leading to increased growth hormone and IGF-1 secretion.
                """,
                "dosage": {
                    "beginner": "12.5mg/day",
                    "intermediate": "20mg/day",
                    "advanced": "25mg/day",
                    "male": "12.5-25mg/day",
                    "female": "10-15mg/day"
                },
                "timing": "Best taken before bed due to sleep-related HGH pulse. Can split dose AM/PM.",
                "cycle": {
                    "length": "16-24 weeks (longer is better)",
                    "off_cycle": "4 weeks minimum",
                    "pct_required": False
                },
                "benefits": [
                    "Increased HGH levels",
                    "Improved sleep quality",
                    "Enhanced muscle recovery",
                    "Better skin health",
                    "Increased appetite",
                    "Joint healing"
                ],
                "side_effects": [
                    "Increased appetite",
                    "Water retention",
                    "Numbness/tingling",
                    "Lethargy (initial)",
                    "Insulin resistance (long-term)"
                ],
                "stacks": [
                    {"compound": "RAD-140", "purpose": "Growth stack"},
                    {"compound": "LGD-4033", "purpose": "Recomp stack"},
                    {"compound": "BPC-157", "purpose": "Healing stack"}
                ],
                "safety": {
                    "risk_level": "moderate",
                    "suppression": "none",
                    "liver_toxicity": "none",
                    "cardiovascular": "possible water retention"
                },
                "evidence_tier": "high",
                "tags": ["hgh", "sleep", "recovery", "healing", "growth"],
                "related": ["HGH", "CJC-1295", "Ipamorelin"]
            },
            
            # ── Peptides ────────────────────────────────────────────────────
            "BPC-157": {
                "name": "BPC-157",
                "category": DomainCategory.PEPTIDES,
                "description": "BPC-157 is a healing peptide with remarkable tissue repair properties for tendons, ligaments, and gut health.",
                "full_description": """
BPC-157 is a stable pentadecapeptide derived from human gastric juice. It's known for powerful healing properties.

KEY CHARACTERISTICS:
• Sequence: BPC-157 (15 amino acids)
• Half-life: ~4 hours (local effect)
• Administration: Subcutaneous injection
• Classification: Healing/Repair Peptide

MECHANISM OF ACTION:
Promotes angiogenesis (new blood vessel growth), upregulates growth hormone receptors, and accelerates wound healing.
                """,
                "dosage": {
                    "general": "250-500mcg 2-3x daily",
                    "injury": "500mcg 3x daily",
                    "maintenance": "250mcg 2x daily",
                    "oral": "500-1000mcg daily (less effective)"
                },
                "timing": "Can be taken any time. Many prefer AM/PM split dosing. Inject subQ in affected area when possible.",
                "cycle": {
                    "length": "4-8 weeks (acute) or 12-16 weeks (chronic)",
                    "off_cycle": "None required",
                    "pct_required": False
                },
                "benefits": [
                    "Accelerated wound healing",
                    "Tendon and ligament repair",
                    "Gut health improvement",
                    "Anti-inflammatory effects",
                    "Reduced joint pain",
                    "Organ protection"
                ],
                "side_effects": [
                    "Nausea (rare)",
                    "Flushing (rare)",
                    "No known significant side effects"
                ],
                "stacks": [
                    {"compound": "TB-500", "purpose": "Maximum healing"},
                    {"compound": "GHK-Cu", "purpose": "Skin and tissue"},
                    {"compound": "MK-677", "purpose": "Enhanced recovery"}
                ],
                "safety": {
                    "risk_level": "low",
                    "suppression": "none",
                    "liver_toxicity": "none",
                    "note": "One of the safest compounds available"
                },
                "evidence_tier": "moderate",
                "tags": ["peptide", "healing", "gut", "tendon", "recovery"],
                "related": ["TB-500", "TB-4", "GHK-Cu"]
            },
            
            "TB-500": {
                "name": "TB-500 (Thymosin Beta-4)",
                "category": DomainCategory.PEPTIDES,
                "description": "TB-500 is a regenerative peptide that promotes cell migration, wound healing, and hair growth.",
                "full_description": """
TB-500 (Thymosin Beta-4) is a naturally occurring peptide with powerful regenerative properties.

KEY CHARACTERISTICS:
• Sequence: Thymosin Beta-4 (43 amino acids)
• Half-life: ~24-48 hours
• Administration: Subcutaneous injection
• Classification: Regenerative Peptide
                """,
                "dosage": {
                    "loading": "4-8mg twice weekly for 4-6 weeks",
                    "maintenance": "2-4mg once weekly",
                    "general": "2-6mg per week"
                },
                "timing": "Can be injected locally or systemically. Morning or evening administration.",
                "cycle": {
                    "length": "6-8 weeks (loading) + 4 weeks maintenance",
                    "off_cycle": "None required",
                    "pct_required": False
                },
                "benefits": [
                    "Wound healing acceleration",
                    "Hair regrowth",
                    "Anti-inflammatory",
                    "Improved flexibility",
                    "Cardiovascular protection",
                    "Nerve regeneration"
                ],
                "side_effects": [
                    "Head rush (occasional)",
                    "Lethargy (temporary)",
                    "No serious side effects reported"
                ],
                "stacks": [
                    {"compound": "BPC-157", "purpose": "Ultimate healing stack"},
                    {"compound": "CJC-1295", "purpose": "Growth stack"}
                ],
                "safety": {
                    "risk_level": "low",
                    "suppression": "none",
                    "liver_toxicity": "none"
                },
                "evidence_tier": "moderate",
                "tags": ["peptide", "healing", "regeneration", "hair", "tissue"],
                "related": ["BPC-157", "Thymosin Alpha-1", "Di-THYβ4"]
            },
            
            # ── Steroids ────────────────────────────────────────────────────
            "Testosterone": {
                "name": "Testosterone",
                "category": DomainCategory.STEROIDS,
                "description": "Testosterone is the primary male sex hormone and the foundation of most anabolic steroid cycles.",
                "full_description": """
Testosterone is the most commonly used anabolic steroid and the benchmark against which all others are measured.

TYPES:
• Enanthate: Half-life 4-7 days
• Cypionate: Half-life 5-8 days
• Propionate: Half-life 2-3 days
• Suspension: Half-life 1 day

MECHANISM OF ACTION:
Binds to androgen receptors throughout the body, promoting protein synthesis and nitrogen retention.
                """,
                "dosage": {
                    "trt": "100-200mg/week",
                    "beginner": "300-400mg/week",
                    "intermediate": "500-600mg/week",
                    "advanced": "750-1000mg/week"
                },
                "timing": "Enanthate/Cypionate: Every 3-4 days. Propionate: Every other day.",
                "cycle": {
                    "length": "12-16 weeks minimum",
                    "off_cycle": "Same duration as cycle",
                    "pct_required": True
                },
                "benefits": [
                    "Massive muscle growth",
                    "Increased strength",
                    "Enhanced recovery",
                    "Improved mood",
                    "Increased libido",
                    "Better sleep"
                ],
                "side_effects": [
                    "Estrogen conversion (bloat, gyno)",
                    "DHT conversion (hair loss, acne)",
                    "HPTA suppression",
                    "Cardiovascular strain",
                    "Natural testosterone shutdown"
                ],
                "stacks": [
                    {"compound": "Nandrolone", "purpose": "Mass building"},
                    {"compound": "Trenbolone", "purpose": "Strength"},
                    {"compound": "Anavar", "purpose": "Cutting"}
                ],
                "pct": {
                    "recommended": "Nolvadex + HCG or HCG + Clomid + Nolvadex",
                    "duration": "8-12 weeks"
                },
                "safety": {
                    "risk_level": "high",
                    "suppression": "severe",
                    "liver_toxicity": "moderate (oral)",
                    "cardiovascular": "significant"
                },
                "evidence_tier": "very_high",
                "tags": ["steroid", "muscle gain", "strength", "base", "foundation"],
                "related": ["Nandrolone", "Trenbolone", "Anavar"]
            },
            
            "Anavar": {
                "name": "Anavar (Oxandrolone)",
                "category": DomainCategory.STEROIDS,
                "description": "Anavar is a mild oral steroid popular for cutting cycles and female use.",
                "full_description": """
Anavar (Oxandrolone) is one of the few steroids considered relatively mild with significant benefits.

KEY CHARACTERISTICS:
• Anabolic: 322-630
• Androgenic: 24
• Half-life: 9-10 hours
• Administration: Oral
• C17-alpha-alkylated (liver toxic)

BEST FOR: Cutting, women, beginners seeking mild effects.
                """,
                "dosage": {
                    "beginner_male": "20-30mg/day",
                    "intermediate_male": "40-50mg/day",
                    "advanced_male": "60-80mg/day",
                    "female": "5-10mg/day (max 20mg)"
                },
                "timing": "Can be taken once or split AM/PM. Take with food to reduce GI issues.",
                "cycle": {
                    "length": "6-8 weeks (due to liver toxicity)",
                    "off_cycle": "4 weeks minimum",
                    "pct_required": "Recommended for higher doses"
                },
                "benefits": [
                    "Lean muscle preservation",
                    "Fat loss assistance",
                    "Increased strength (without water retention)",
                    "Dry gains",
                    "Female-friendly"
                ],
                "side_effects": [
                    "Liver toxicity (elevated enzymes)",
                    "Negative lipid profile",
                    "HPTA suppression (high doses)",
                    "Hair loss (in predisposed)",
                    "Virilization in women"
                ],
                "stacks": [
                    {"compound": "Testosterone", "purpose": "Mass building"},
                    {"compound": "Winstrol", "purpose": "Hardening"},
                    {"compound": "Primobolan", "purpose": "Mild cutting"}
                ],
                "safety": {
                    "risk_level": "moderate",
                    "suppression": "mild to moderate",
                    "liver_toxicity": "significant (monitor)",
                    "cardiovascular": "moderate"
                },
                "evidence_tier": "high",
                "tags": ["steroid", "cutting", "mild", "oral", "female-friendly"],
                "related": ["Winstrol", "Primobolan", "Superdrol"]
            },
            
            # ── Supplements ────────────────────────────────────────────────
            "Creatine": {
                "name": "Creatine Monohydrate",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Creatine is the most researched sports supplement with proven benefits for strength and power output.",
                "full_description": """
Creatine Monohydrate is the gold standard supplement for increasing strength and power output.

MECHANISM:
• Increases ATP regeneration
• Enhances phosphocreatine stores
• Improves high-intensity performance

FORMS:
• Monohydrate (most researched)
• HCL (more soluble)
• Ethyl Ester (debated efficacy)
                """,
                "dosage": {
                    "loading": "20g/day (4x5g) for 5-7 days",
                    "maintenance": "3-5g/day",
                    "optimal": "0.03g per lb bodyweight"
                },
                "timing": "Any time. Post-workout may be slightly better. Can take with carbs for uptake.",
                "cycle": {
                    "length": "Can be taken year-round",
                    "off_cycle": "Not necessary (natural compound)"
                },
                "benefits": [
                    "Increased strength",
                    "Enhanced power output",
                    "Faster muscle recovery",
                    "Increased muscle cell hydration",
                    "Cognitive benefits",
                    "Low cost"
                ],
                "side_effects": [
                    "Water retention (transient)",
                    "Digestive issues (rare)",
                    "Weight gain (water)"
                ],
                "stacks": [
                    {"compound": "Beta-Alanine", "purpose": "Endurance"},
                    {"compound": "Caffeine", "purpose": "Pre-workout"},
                    {"compound": "Whey Protein", "purpose": "Muscle building"}
                ],
                "safety": {
                    "risk_level": "very_safe",
                    "suppression": "none",
                    "liver_toxicity": "none",
                    "kidney": "Safe in healthy individuals"
                },
                "evidence_tier": "very_high",
                "tags": ["supplement", "strength", "power", "beginner", "essential"],
                "related": ["Beta-Alanine", "Caffeine", "Whey Protein"]
            },
            
            "Whey Protein": {
                "name": "Whey Protein",
                "category": DomainCategory.SUPPLEMENTS,
                "description": "Whey protein is a fast-absorbing complete protein essential for muscle protein synthesis.",
                "full_description": """
Whey Protein is the most popular protein supplement derived from milk during cheese production.

TYPES:
• Concentrate (70-80% protein)
• Isolate (90%+ protein)
• Hydrolysate (pre-digested)

AMINO ACID PROFILE:
• Complete protein (all essential AAs)
• High leucine content (~11%)
• Fast absorption
                """,
                "dosage": {
                    "general": "20-40g post-workout",
                    "daily_target": "1.6-2.2g per kg bodyweight",
                    "per_serving": "20-40g depending on needs"
                },
                "timing": "Post-workout is optimal for MPS. Can also be used as meal supplement.",
                "cycle": {
                    "length": "Continuous use",
                    "off_cycle": "Not necessary"
                },
                "benefits": [
                    "Fast muscle protein synthesis",
                    "Convenient protein source",
                    "Complete amino acid profile",
                    "Supports recovery",
                    "Versatile (shakes, baking, cooking)"
                ],
                "side_effects": [
                    "Lactose intolerance issues",
                    "Digestive discomfort",
                    "Bloating"
                ],
                "stacks": [
                    {"compound": "Creatine", "purpose": "Muscle building"},
                    {"compound": "Casein", "purpose": "Nighttime protein"},
                    {"compound": "Carbs", "purpose": "Post-workout stack"}
                ],
                "safety": {
                    "risk_level": "very_safe",
                    "suppression": "none",
                    "note": "One of the safest supplements"
                },
                "evidence_tier": "very_high",
                "tags": ["supplement", "protein", "nutrition", "recovery", "essential"],
                "related": ["Casein", "Egg Protein", "Plant Protein"]
            }
        }
    
    def _build_exercise_database(self):
        """Build exercise database"""
        self.exercises = {
            "chest": {
                "compound": ["Bench Press", "Incline Bench", "Decline Bench"],
                "isolation": ["Dumbbell Flyes", "Cable Crossover", "Pec Deck"],
                "push": ["Push-ups", "Dips"],
                "tips": "Focus on full range of motion. Squeeze at contraction."
            },
            "back": {
                "compound": ["Deadlift", "Barbell Row", "Pull-ups", "Lat Pulldown"],
                "isolation": ["Cable Row", "Face Pulls", "Lat Pullover"],
                "tips": "Initiate with lats, not arms. Keep core tight."
            },
            "legs": {
                "compound": ["Squat", "Leg Press", "Romanian Deadlift", "Leg Curl"],
                "isolation": ["Leg Extension", "Calf Raises", "Hip Thrust"],
                "tips": "Full depth on squats. Control the eccentric."
            },
            "shoulders": {
                "compound": ["Overhead Press", "Push Press"],
                "isolation": ["Lateral Raise", "Front Raise", "Rear Delt Flye"],
                "tips": "Light weight, high rep for delts."
            },
            "arms": {
                "biceps": ["Barbell Curl", "Dumbbell Curl", "Hammer Curl", "Preacher Curl"],
                "triceps": ["Tricep Pushdown", "Skull Crushers", "Close-Grip Bench"],
                "tips": "Control the negative. Don't swing."
            }
        }
    
    def _build_nutrition_database(self):
        """Build nutrition database"""
        self.nutrition = {
            "macros": {
                "protein": {
                    "recommendation": "1.6-2.2g per kg bodyweight",
                    "for_muscle_gain": "2.2-3.3g per kg (advanced)",
                    "for_fat_loss": "2.2-3.3g per kg (preserve muscle)"
                },
                "carbs": {
                    "low": "0.5-1g per kg bodyweight",
                    "moderate": "2-3g per kg bodyweight",
                    "high": "4-6g per kg bodyweight"
                },
                "fats": {
                    "minimum": "0.5g per kg bodyweight",
                    "optimal": "0.7-1g per kg bodyweight"
                }
            },
            "calories": {
                "maintenance": "bodyweight x 15-18 (moderate activity)",
                "bulking": "maintenance + 250-500",
                "cutting": "maintenance - 500"
            },
            "meal_timing": {
                "protein": "Every 3-4 hours or 20-40g post-workout",
                "pre_workout": "1-2 hours before training",
                "post_workout": "Within 2 hours (anabolic window)",
                "bedtime": "Casein or slow-digesting protein"
            }
        }
    
    def _build_supplement_database(self):
        """Build supplement reference database"""
        self.supplements = {
            "essential": ["Creatine", "Protein", "Vitamin D", "Fish Oil"],
            "performance": ["Caffeine", "Beta-Alanine", "Citrulline", "BCAAs"],
            "recovery": ["ZMA", "Magnesium", "Collagen", "Glutamine"],
            "health": ["Multivitamin", "Vitamin C", "Zinc", "Ashwagandha"]
        }
    
    def _build_protocol_database(self):
        """Build cycle and protocol database"""
        self.protocols = {
            "sarms_beginner": {
                "compound": "Ostarine",
                "dosage": "15mg/day",
                "duration": "8 weeks",
                "pct": "Not required",
                "notes": "Most mild and research-backed"
            },
            "sarms_intermediate": {
                "stack": ["RAD-140", "LGD-4033"],
                "dosage": "RAD-140 10mg + LGD-4033 5mg",
                "duration": "10 weeks",
                "pct": "Required - Nolvadex",
                "notes": "Significant gains, expect suppression"
            },
            "steroid_beginner": {
                "compound": "Testosterone Enanthate",
                "dosage": "300-400mg/week",
                "duration": "12 weeks",
                "pct": "Required - Nolvadex + HCG",
                "notes": "Foundation of most cycles"
            },
            "cutting_stack": {
                "stack": ["Ostarine 20mg", "Cardarine 20mg", "S4 50mg"],
                "duration": "8 weeks",
                "notes": "Preserve muscle, enhance fat loss"
            },
            "pct_protocol": {
                "nolvadex": "40/20/20/20mg (2 weeks each)",
                "clomid": "50/25/25/25mg (2 weeks each)",
                "hcg": "1000IU EOD for 3 weeks",
                "duration": "4-6 weeks"
            }
        }
    
    def process(self, query_understanding) -> List[KnowledgeResult]:
        """Search knowledge base based on query understanding"""
        results = []
        compound = query_understanding.compound
        domain = query_understanding.domain
        intent = query_understanding.intent
        
        # Search by compound name
        if compound and compound in self.compounds:
            data = self.compounds[compound]
            results.append(KnowledgeResult(
                id=compound,
                name=data["name"],
                category=data["category"],
                content=data,
                relevance_score=0.95
            ))
        
        # Search by domain
        for name, data in self.compounds.items():
            if data["category"] == domain and name != compound:
                if self._matches_intent(data, intent):
                    results.append(KnowledgeResult(
                        id=name,
                        name=data["name"],
                        category=data["category"],
                        content=data,
                        relevance_score=0.8
                    ))
        
        # Keyword search in compounds
        query = query_understanding.original_query.lower()
        for name, data in self.compounds.items():
            if name not in [r.name for r in results]:
                for tag in data.get("tags", []):
                    if tag in query:
                        results.append(KnowledgeResult(
                            id=name,
                            name=data["name"],
                            category=data["category"],
                            content=data,
                            relevance_score=0.7
                        ))
                        break
        
        return results
    
    def _matches_intent(self, data: Dict, intent) -> bool:
        """Check if compound data matches query intent"""
        intent_str = intent.value if hasattr(intent, 'value') else str(intent)
        tags = data.get("tags", [])
        
        if intent_str == "benefits" and "muscle gain" in tags:
            return True
        if intent_str == "cutting" and "cutting" in tags:
            return True
        if intent_str == "beginner" and "beginner" in tags:
            return True
        
        return False


# Singleton
agent = KnowledgeBaseAgent()

def search_knowledge_base(query_understanding) -> List[KnowledgeResult]:
    """Search knowledge base"""
    return agent.process(query_understanding)
