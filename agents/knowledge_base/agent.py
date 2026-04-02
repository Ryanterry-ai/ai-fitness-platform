"""
Knowledge Base Agent
====================
Searches the internal knowledge base for fitness, supplements, and compounds.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from models import KnowledgeResult, DomainCategory, QueryUnderstanding


class KnowledgeBaseAgent:
    """
    Agent responsible for searching the internal knowledge base.
    
    Responsibilities:
    - Search compound database
    - Search supplement profiles
    - Search exercise knowledge graph
    - Search SEO queries database
    - Search topic clusters
    - Return relevant documents with relevance scores
    """
    
    def __init__(self, kb_path: Optional[str] = None):
        self.kb_path = kb_path or self._get_default_kb_path()
        self.knowledge_base = self._load_knowledge_base()
        self.compound_index = self._build_compound_index()
        self.topic_index = self._build_topic_index()
    
    def _get_default_kb_path(self) -> str:
        """Get default knowledge base path"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge_base"
        )
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base data"""
        kb_file = os.path.join(self.kb_path, "knowledge.json")
        
        if os.path.exists(kb_file):
            with open(kb_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Return default knowledge base if file doesn't exist
        return self._get_default_knowledge()
    
    def _get_default_knowledge(self) -> Dict[str, Any]:
        """Return default embedded knowledge base"""
        return {
            "compounds": self._get_compound_profiles(),
            "exercises": self._get_exercise_profiles(),
            "nutrition": self._get_nutrition_profiles(),
            "general_topics": self._get_general_topics()
        }
    
    def _get_compound_profiles(self) -> List[Dict[str, Any]]:
        """Return compound profiles"""
        return [
            {
                "id": "creatine",
                "name": "Creatine Monohydrate",
                "aliases": ["creatine", "creatina", "kreatin"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["strength", "muscle_gain", "beginner", "evidence_high"],
                "summary": "Most researched ergogenic aid for strength and power.",
                "what_it_is": "Creatine monohydrate is a naturally occurring compound that increases phosphocreatine stores in muscles, enabling faster ATP regeneration during high-intensity exercise.",
                "dosage": "3-5g/day maintenance. Optional loading: 20g/day for 5-7 days.",
                "timing": "Any time of day, consistency most important.",
                "evidence_tier": "very_high",
                "safe_for_beginners": True,
                "benefits": ["Increased strength", "Improved power output", "Faster recovery"],
                "side_effects": ["Mild water retention"],
                "risks": "Very low risk, well-studied supplement."
            },
            {
                "id": "rad140",
                "name": "RAD-140 (Testolone)",
                "aliases": ["rad140", "rad-140", "testolone"],
                "category": "sarms",
                "domain": "sarms",
                "tags": ["muscle_gain", "strength", "sarm"],
                "summary": "Highly anabolic SARM with strong androgenic activity.",
                "what_it_is": "RAD-140 is a selective androgen receptor modulator (SARM) that demonstrates high anabolic activity with relatively low androgenic side effects.",
                "dosage": "10-20mg/day for 8-12 weeks.",
                "timing": "Once daily, preferably with food.",
                "evidence_tier": "moderate",
                "safe_for_beginners": False,
                "benefits": ["Significant lean mass gains", "Improved strength", "Fat loss support"],
                "side_effects": ["Testosterone suppression", "Potential liver stress", "HDL reduction"],
                "risks": "Moderate risk. Requires PCT. Not approved for human consumption.",
                "legal_status": "Research chemical - not FDA approved"
            },
            {
                "id": "lgd4033",
                "name": "LGD-4033 (Ligandrol)",
                "aliases": ["lgd4033", "lgd-4033", "ligandrol"],
                "category": "sarms",
                "domain": "sarms",
                "tags": ["muscle_gain", "bulking", "sarm"],
                "summary": "Potent SARM for lean mass accumulation.",
                "what_it_is": "LGD-4033 is a potent nonsteroidal SARM that selectively binds androgen receptors in muscle and bone.",
                "dosage": "5-10mg/day for 8-12 weeks.",
                "timing": "Once daily in the morning.",
                "evidence_tier": "moderate",
                "safe_for_beginners": False,
                "benefits": ["Significant muscle mass gains", "Improved strength", "Bone health"],
                "side_effects": ["Testosterone suppression", "Fatigue", "Headache"],
                "risks": "Moderate risk. Requires bloodwork and PCT.",
                "legal_status": "Research chemical"
            },
            {
                "id": "ostarine",
                "name": "Ostarine (MK-2866)",
                "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm"],
                "category": "sarms",
                "domain": "sarms",
                "tags": ["recomp", "fat_loss", "sarm", "beginner"],
                "summary": "Mildest SARM, ideal for recomposition.",
                "what_it_is": "Ostarine is the mildest and most researched SARM, suitable for beginners looking for lean muscle preservation.",
                "dosage": "10-25mg/day for 8-12 weeks.",
                "timing": "Once daily.",
                "evidence_tier": "moderate",
                "safe_for_beginners": True,
                "benefits": ["Mild muscle building", "Fat loss support", "Joint healing"],
                "side_effects": ["Mild testosterone suppression", "HDL reduction"],
                "risks": "Lower risk than other SARMs, but still requires monitoring.",
                "legal_status": "Research chemical"
            },
            {
                "id": "mk677",
                "name": "MK-677 (Ibutamoren)",
                "aliases": ["mk677", "mk-677", "ibutamoren"],
                "category": "sarms",
                "domain": "sarms",
                "tags": ["muscle_gain", "recovery", "hgh", "sleep"],
                "summary": "Oral GH secretagogue that stimulates growth hormone.",
                "what_it_is": "MK-677 is a ghrelin receptor agonist that stimulates natural GH and IGF-1 secretion without suppressing testosterone.",
                "dosage": "10-25mg/day before bed.",
                "timing": "Before bed (aligns with natural GH pulse).",
                "evidence_tier": "moderate",
                "safe_for_beginners": True,
                "benefits": ["Elevated GH/IGF-1", "Improved sleep", "Lean mass support", "Recovery enhancement"],
                "side_effects": ["Increased appetite", "Water retention", "Elevated blood glucose"],
                "risks": "Low suppression risk. Monitor blood sugar if diabetic.",
                "legal_status": "Research chemical"
            },
            {
                "id": "testosterone",
                "name": "Testosterone Enanthate",
                "aliases": ["testosterone", "test e", "testosterone enanthate"],
                "category": "steroids",
                "domain": "steroids",
                "tags": ["muscle_gain", "bulking", "steroid", "gold_standard"],
                "summary": "Gold standard anabolic steroid for mass and strength.",
                "what_it_is": "Testosterone enanthate is a long-ester injectable testosterone, the gold standard for anabolic steroid cycles.",
                "dosage": "300-500mg/week (beginner), 500-750mg/week (intermediate).",
                "timing": "IM injection every 3.5 days.",
                "evidence_tier": "very_high",
                "safe_for_beginners": False,
                "benefits": ["Significant muscle mass", "Major strength gains", "Improved libido", "Enhanced recovery"],
                "side_effects": ["Testosterone suppression", "Aromatization", "Gynecomastia risk", "Cardiovascular strain"],
                "risks": "High risk. Requires AI, PCT, bloodwork, and medical supervision.",
                "legal_status": "Schedule III controlled substance (USA)"
            },
            {
                "id": "anavar",
                "name": "Anavar (Oxandrolone)",
                "aliases": ["anavar", "oxandrolone", "var"],
                "category": "steroids",
                "domain": "steroids",
                "tags": ["fat_loss", "cutting", "steroid", "mild"],
                "summary": "Mild oral steroid ideal for cutting.",
                "what_it_is": "Anavar is a mild oral anabolic steroid popular for cutting phases and preserving muscle in a deficit.",
                "dosage": "20-80mg/day (men), 5-20mg/day (women).",
                "timing": "Split doses throughout the day.",
                "evidence_tier": "high",
                "safe_for_beginners": False,
                "benefits": ["Muscle preservation during cuts", "Strength without bulk", "Minimal water retention"],
                "side_effects": ["Liver stress (oral)", "HDL reduction", "Lipid changes"],
                "risks": "Moderate risk. Liver support and bloodwork required.",
                "legal_status": "Schedule III controlled substance"
            },
            {
                "id": "bpc157",
                "name": "BPC-157",
                "aliases": ["bpc157", "bpc-157", "body protection compound"],
                "category": "peptides",
                "domain": "peptides",
                "tags": ["recovery", "healing", "injury", "gut", "peptide"],
                "summary": "Healing peptide for tissue repair.",
                "what_it_is": "BPC-157 is a pentadecapeptide derived from human gastric juice that promotes healing of tendons, ligaments, muscles, and gut.",
                "dosage": "250-500mcg/day subcutaneous or intramuscular.",
                "timing": "Near injury site or systemic, 1-2x daily.",
                "evidence_tier": "moderate",
                "safe_for_beginners": True,
                "benefits": ["Accelerated tendon/ligament healing", "Gut lining repair", "Anti-inflammatory"],
                "side_effects": ["Minor injection site irritation"],
                "risks": "Low risk. Source quality is critical.",
                "legal_status": "Research chemical"
            },
            {
                "id": "hgh",
                "name": "Human Growth Hormone (HGH)",
                "aliases": ["hgh", "growth hormone", "somatropin", "gh"],
                "category": "peptides",
                "domain": "hgh",
                "tags": ["anti_aging", "muscle_gain", "fat_loss", "recovery"],
                "summary": "Potent lipolytic and anabolic hormone.",
                "what_it_is": "HGH (somatropin) is a 191-amino acid peptide hormone that stimulates IGF-1 production and promotes lipolysis.",
                "dosage": "1-3 IU/day (anti-aging), 4-8 IU/day (bodybuilding).",
                "timing": "SubQ injection on waking or before bed.",
                "evidence_tier": "very_high",
                "safe_for_beginners": False,
                "benefits": ["Visceral fat reduction", "Lean mass retention", "Improved sleep", "Skin health"],
                "side_effects": ["Carpal tunnel", "Insulin resistance", "Water retention"],
                "risks": "High risk. Requires physician supervision and bloodwork.",
                "legal_status": "Prescription only worldwide"
            },
            {
                "id": "whey",
                "name": "Whey Protein",
                "aliases": ["whey", "whey protein", "protein powder"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["muscle_gain", "recovery", "protein", "beginner"],
                "summary": "Fast-digesting protein for post-workout recovery.",
                "what_it_is": "Whey protein is the gold standard protein supplement, rich in leucine for optimal muscle protein synthesis.",
                "dosage": "25-50g per serving, 1-2x daily.",
                "timing": "Post-workout is optimal, or to meet daily protein targets.",
                "evidence_tier": "very_high",
                "safe_for_beginners": True,
                "benefits": ["Fast absorption", "Complete amino acid profile", "High leucine content"],
                "side_effects": ["GI discomfort if lactose intolerant"],
                "risks": "Very low risk. Use isolate if lactose intolerant.",
                "types": [
                    {"name": "Whey Concentrate", "protein": "70-80%", "best_for": "General use"},
                    {"name": "Whey Isolate", "protein": "90%+", "best_for": "Cutting, lactose intolerant"},
                    {"name": "Whey Hydrolysate", "protein": "95%+", "best_for": "Fastest absorption"}
                ]
            },
            {
                "id": "caffeine",
                "name": "Caffeine",
                "aliases": ["caffeine", "pre-workout", "stimulant"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["strength", "endurance", "fat_loss", "focus", "pre_workout"],
                "summary": "Most studied ergogenic aid for performance.",
                "what_it_is": "Caffeine is an adenosine receptor antagonist that reduces perceived exertion and improves power output.",
                "dosage": "3-6mg/kg bodyweight (200-400mg typical).",
                "timing": "30-60 minutes pre-workout. Avoid within 6 hours of sleep.",
                "evidence_tier": "very_high",
                "safe_for_beginners": True,
                "benefits": ["Increased power output", "Improved endurance", "Enhanced fat oxidation", "Mental focus"],
                "side_effects": ["Tolerance development", "Sleep disruption", "Anxiety at high doses"],
                "risks": "Moderate. Cycle off to prevent tolerance.",
                "stacking": "Stack with L-Theanine (200mg) for smooth focus"
            },
            {
                "id": "citrulline",
                "name": "L-Citrulline / Citrulline Malate",
                "aliases": ["citrulline", "l-citrulline", "citrulline malate", "pump"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["pump", "endurance", "pre_workout", "blood_flow"],
                "summary": "NO precursor for muscle pump and endurance.",
                "what_it_is": "L-Citrulline converts to arginine in kidneys, then to nitric oxide for vasodilation and improved blood flow.",
                "dosage": "L-Citrulline: 6-8g. Citrulline Malate 2:1: 8g.",
                "timing": "30-60 minutes pre-workout.",
                "evidence_tier": "high",
                "safe_for_beginners": True,
                "benefits": ["Muscle pump", "Reduced DOMS", "Improved endurance", "Blood pressure support"],
                "side_effects": ["GI discomfort at high doses"],
                "risks": "Very low risk."
            },
            {
                "id": "beta_alanine",
                "name": "Beta-Alanine",
                "aliases": ["beta alanine", "beta-alanine", "carnosine"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["endurance", "strength", "pre_workout"],
                "summary": "Amino acid that buffers muscle acidity.",
                "what_it_is": "Beta-alanine is a non-essential amino acid that raises muscle carnosine levels to buffer H+ ions during intense exercise.",
                "dosage": "3.2-6.4g/day split into doses to reduce tingling.",
                "timing": "Pre-workout or throughout day.",
                "evidence_tier": "high",
                "safe_for_beginners": True,
                "benefits": ["Delayed muscle fatigue", "Higher rep capacity", "Improved endurance"],
                "side_effects": ["Tingling/paresthesia (harmless)"],
                "risks": "Very low. Split doses to minimize tingling."
            },
            {
                "id": "vitamin_d",
                "name": "Vitamin D3 + K2",
                "aliases": ["vitamin d", "vitamin d3", "cholecalciferol"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["testosterone", "immune", "bone", "recovery", "health"],
                "summary": "Essential vitamin-hormone for overall health.",
                "what_it_is": "Vitamin D3 is a fat-soluble prohormone that regulates calcium, immune function, and testosterone production.",
                "dosage": "D3: 2000-5000 IU/day. K2: 100-200mcg/day.",
                "timing": "With largest fat-containing meal.",
                "evidence_tier": "very_high",
                "safe_for_beginners": True,
                "benefits": ["Testosterone support", "Immune function", "Bone health", "Mood improvement"],
                "side_effects": ["Toxicity only at very high doses without monitoring"],
                "risks": "Very low. Test levels first."
            },
            {
                "id": "omega3",
                "name": "Omega-3 Fish Oil (EPA + DHA)",
                "aliases": ["omega 3", "fish oil", "omega-3", "epa", "dha"],
                "category": "supplements",
                "domain": "supplements",
                "tags": ["recovery", "anti_inflammatory", "cardiovascular", "joint"],
                "summary": "Essential fatty acids for anti-inflammation.",
                "what_it_is": "Omega-3 EPA and DHA reduce systemic inflammation, improve cardiovascular markers, and support recovery.",
                "dosage": "3-6g combined EPA+DHA per day.",
                "timing": "With meals.",
                "evidence_tier": "very_high",
                "safe_for_beginners": True,
                "benefits": ["Anti-inflammatory", "Cardiovascular protection", "Joint health", "MPS support"],
                "side_effects": ["Fish aftertaste"],
                "risks": "Very low. Check EPA+DHA content on label."
            },
            {
                "id": "nandrolone",
                "name": "Nandrolone (NPP/Deca)",
                "aliases": ["nandrolone", "deca", "npp", "deca durabolin"],
                "category": "steroids",
                "domain": "steroids",
                "tags": ["muscle_gain", "joint_health", "steroid"],
                "summary": "19-nor anabolic for mass and joint support.",
                "what_it_is": "Nandrolone is a 19-nortestosterone derivative known for lean mass gains and joint lubrication.",
                "dosage": "NPP: 300-400mg/week. Deca: 200-400mg/week.",
                "timing": "IM injection on schedule. Always with testosterone base.",
                "evidence_tier": "high",
                "safe_for_beginners": False,
                "benefits": ["Lean mass gains", "Joint lubrication", "Collagen synthesis"],
                "side_effects": ["Prolactin elevation", "Testosterone suppression", "Sexual dysfunction"],
                "risks": "High risk. Requires cabergoline for prolactin control.",
                "legal_status": "Schedule III controlled substance"
            }
        ]
    
    def _get_exercise_profiles(self) -> List[Dict[str, Any]]:
        """Return exercise profiles"""
        return [
            {
                "id": "squat",
                "name": "Barbell Squat",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["compound", "legs", "mass", "strength"],
                "muscles": ["Quadriceps", "Glutes", "Hamstrings", "Core"],
                "evidence_tier": "very_high",
                "best_for": "Overall lower body development and mass",
                "setup": "Bar on upper back, feet shoulder-width, braced core",
                "cues": ["Knees track over toes", "Chest up", "Depth to parallel or below"]
            },
            {
                "id": "deadlift",
                "name": "Conventional Deadlift",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["compound", "full_body", "strength", "mass"],
                "muscles": ["Back", "Hamstrings", "Glutes", "Traps", "Core"],
                "evidence_tier": "very_high",
                "best_for": "Total body strength and posterior chain development",
                "setup": "Bar over mid-foot, hinge at hips, mixed or double overhand grip",
                "cues": ["Neutral spine", "Chest up", "Drive through heels"]
            },
            {
                "id": "bench_press",
                "name": "Barbell Bench Press",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["compound", "chest", "strength", "mass"],
                "muscles": ["Chest", "Shoulders", "Triceps"],
                "evidence_tier": "very_high",
                "best_for": "Upper body pushing strength and chest development",
                "setup": "Eyes under bar, feet flat, retract shoulder blades",
                "cues": ["Touch chest lightly", "Drive feet", "Press in arc"]
            }
        ]
    
    def _get_nutrition_profiles(self) -> List[Dict[str, Any]]:
        """Return nutrition profiles"""
        return [
            {
                "id": "protein_intake",
                "name": "Protein Requirements",
                "category": "nutrition",
                "domain": "nutrition",
                "tags": ["protein", "muscle_gain", "fat_loss", "macros"],
                "summary": "Optimal protein intake for body composition",
                "recommendations": {
                    "muscle_gain": "1.6-2.2g/kg bodyweight",
                    "fat_loss": "2.0-2.4g/kg bodyweight",
                    "maintenance": "1.6-2.0g/kg bodyweight"
                },
                "timing": "Distribute across 4-5 meals, 30-40g per meal",
                "evidence_tier": "very_high"
            },
            {
                "id": "calorie_calculation",
                "name": "TDEE Calculation",
                "category": "nutrition",
                "domain": "nutrition",
                "tags": ["calories", "tdee", "deficit", "surplus"],
                "summary": "Calculating Total Daily Energy Expenditure",
                "formula": "BMR × Activity Multiplier = TDEE",
                "activity_multipliers": {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "very_active": 1.9
                },
                "evidence_tier": "very_high"
            }
        ]
    
    def _get_general_topics(self) -> List[Dict[str, Any]]:
        """Return general topic profiles"""
        return [
            {
                "id": "fat_loss_exercise",
                "name": "Fat Loss Exercises",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["fat_loss", "cardio", "hiit", "resistance"],
                "summary": "Evidence-based exercise selection for fat loss",
                "best_exercises": ["Resistance Training", "HIIT", "Steady-State Cardio", "Walking"],
                "evidence_tier": "very_high"
            },
            {
                "id": "muscle_gain_training",
                "name": "Muscle Gain Training",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["muscle_gain", "hypertrophy", "training", "progressive_overload"],
                "summary": "Science-based hypertrophy training",
                "principles": ["Mechanical tension", "Metabolic stress", "Progressive overload"],
                "evidence_tier": "very_high"
            },
            {
                "id": "beginner_workout",
                "name": "Beginner Workout Guide",
                "category": "exercise",
                "domain": "exercise",
                "tags": ["beginner", "foundation", "compound_movements"],
                "summary": "Starter guide for those new to training",
                "recommendations": ["Full body 3x/week", "Compound movements", "Linear progression"],
                "evidence_tier": "very_high"
            }
        ]
    
    def _build_compound_index(self) -> Dict[str, int]:
        """Build index for fast compound lookup"""
        index = {}
        compounds = self.knowledge_base.get("compounds", [])
        for i, compound in enumerate(compounds):
            index[compound["id"]] = i
            for alias in compound.get("aliases", []):
                index[alias.lower()] = i
        return index
    
    def _build_topic_index(self) -> Dict[str, List[int]]:
        """Build index for topic lookup"""
        index = {}
        
        # Index general topics
        topics = self.knowledge_base.get("general_topics", [])
        for i, topic in enumerate(topics):
            for tag in topic.get("tags", []):
                if tag not in index:
                    index[tag] = []
                index[tag].append(i)
        
        return index
    
    def process(self, query_understanding) -> List[KnowledgeResult]:
        """
        Search the knowledge base based on query understanding.
        
        Args:
            query_understanding: Parsed query from QueryUnderstandingAgent
            
        Returns:
            List of KnowledgeResult objects sorted by relevance
        """
        results = []
        
        # Get primary compound
        compound = query_understanding.compound
        domain = query_understanding.domain
        entities = query_understanding.entities
        goal = query_understanding.goal
        
        # Search compounds
        if compound:
            compound_results = self._search_compounds(compound, query_understanding)
            results.extend(compound_results)
        
        # Search by domain
        domain_results = self._search_by_domain(domain, query_understanding)
        results.extend(domain_results)
        
        # Search exercises if relevant
        if domain == "exercise" or query_understanding.intent.value == "exercise":
            exercise_results = self._search_exercises(query_understanding)
            results.extend(exercise_results)
        
        # Search nutrition if relevant
        if domain == "nutrition" or query_understanding.intent.value == "nutrition":
            nutrition_results = self._search_nutrition(query_understanding)
            results.extend(nutrition_results)
        
        # Search general topics
        topic_results = self._search_topics(query_understanding)
        results.extend(topic_results)
        
        # Sort by relevance and deduplicate
        results = self._deduplicate_and_sort(results)
        
        return results[:10]  # Return top 10 results
    
    def _search_compounds(self, compound_name: str, 
                         query_understanding) -> List[KnowledgeResult]:
        """Search for compound in knowledge base"""
        results = []
        compounds = self.knowledge_base.get("compounds", [])
        
        compound_lower = compound_name.lower().replace("-", "").replace(" ", "")
        
        for compound in compounds:
            # Check name and aliases
            names_to_check = [compound["name"].lower()] + [
                a.lower() for a in compound.get("aliases", [])
            ]
            
            for name in names_to_check:
                name_clean = name.lower().replace("-", "").replace(" ", "")
                if compound_lower in name_clean or name_clean in compound_lower:
                    score = self._calculate_relevance(compound, query_understanding)
                    results.append(KnowledgeResult(
                        id=compound["id"],
                        name=compound["name"],
                        category=DomainCategory(compound.get("domain", "general")),
                        content=compound,
                        relevance_score=score,
                        source="compound_db"
                    ))
                    break
        
        return results
    
    def _search_by_domain(self, domain: DomainCategory, 
                          query_understanding) -> List[KnowledgeResult]:
        """Search knowledge base by domain category"""
        results = []
        compounds = self.knowledge_base.get("compounds", [])
        
        domain_str = domain.value if hasattr(domain, 'value') else str(domain)
        
        for compound in compounds:
            if compound.get("domain") == domain_str:
                score = self._calculate_relevance(compound, query_understanding) * 0.7
                results.append(KnowledgeResult(
                    id=compound["id"],
                    name=compound["name"],
                    category=DomainCategory(compound.get("domain", "general")),
                    content=compound,
                    relevance_score=score,
                    source="compound_db"
                ))
        
        return results
    
    def _search_exercises(self, query_understanding) -> List[KnowledgeResult]:
        """Search exercise profiles"""
        results = []
        exercises = self.knowledge_base.get("exercises", [])
        
        for exercise in exercises:
            score = self._calculate_relevance(exercise, query_understanding)
            if score > 0.1:
                results.append(KnowledgeResult(
                    id=exercise["id"],
                    name=exercise["name"],
                    category=DomainCategory.EXERCISE,
                    content=exercise,
                    relevance_score=score,
                    source="exercise_db"
                ))
        
        return results
    
    def _search_nutrition(self, query_understanding) -> List[KnowledgeResult]:
        """Search nutrition profiles"""
        results = []
        nutrition = self.knowledge_base.get("nutrition", [])
        
        for item in nutrition:
            score = self._calculate_relevance(item, query_understanding)
            if score > 0.1:
                results.append(KnowledgeResult(
                    id=item["id"],
                    name=item["name"],
                    category=DomainCategory.NUTRITION,
                    content=item,
                    relevance_score=score,
                    source="nutrition_db"
                ))
        
        return results
    
    def _search_topics(self, query_understanding) -> List[KnowledgeResult]:
        """Search general topics"""
        results = []
        topics = self.knowledge_base.get("general_topics", [])
        
        for topic in topics:
            score = self._calculate_relevance(topic, query_understanding)
            if score > 0.2:
                results.append(KnowledgeResult(
                    id=topic["id"],
                    name=topic["name"],
                    category=DomainCategory.GENERAL,
                    content=topic,
                    relevance_score=score,
                    source="topic_db"
                ))
        
        return results
    
    def _calculate_relevance(self, item: Dict[str, Any], 
                            query_understanding) -> float:
        """Calculate relevance score for an item"""
        score = 0.5
        
        # Check tags
        item_tags = [t.lower() for t in item.get("tags", [])]
        
        # Goal match
        goal = query_understanding.goal
        if goal and any(goal.lower() in tag for tag in item_tags):
            score += 0.2
        
        # Domain match
        if item.get("domain") == query_understanding.domain.value:
            score += 0.15
        
        # Intent match
        intent = query_understanding.intent.value
        if any(intent.lower() in tag for tag in item_tags):
            score += 0.1
        
        # Safe for beginners
        if query_understanding.experience_level == "beginner":
            if item.get("safe_for_beginners", False):
                score += 0.1
        
        return min(score, 1.0)
    
    def _deduplicate_and_sort(self, results: List[KnowledgeResult]) -> List[KnowledgeResult]:
        """Remove duplicates and sort by relevance"""
        seen = set()
        unique_results = []
        
        for result in results:
            if result.id not in seen:
                seen.add(result.id)
                unique_results.append(result)
        
        return sorted(unique_results, key=lambda x: x.relevance_score, reverse=True)


# Singleton instance
knowledge_base_agent = KnowledgeBaseAgent()


def search_knowledge_base(query_understanding: QueryUnderstanding) -> List[KnowledgeResult]:
    """
    Convenience function to search knowledge base.
    
    Args:
        query_understanding: Parsed query from QueryUnderstandingAgent
        
    Returns:
        List of KnowledgeResult objects
    """
    return knowledge_base_agent.process(query_understanding)
