# ⚡ FitSearch AI — World-Class Fitness Intelligence Engine v6

A production-grade AI-powered search engine for fitness, bodybuilding, supplements, steroids, SARMs, peptides, HGH, exercises, nutrition, and performance compounds.

## 🚀 Features

### Core Search Engine
- **17-Section Structured Reports** — Every search returns comprehensive research cards
- **AI-Enhanced Responses** — Claude AI enriches knowledge base with latest research
- **PubMed Integration** — Live research paper retrieval via NCBI API
- **Examine.com Links** — Auto-linked to Examine.com supplement data
- **Smart Caching** — SQLite-based 24h cache for instant repeat queries
- **Intent Detection** — Understands dosage/cycle/research/product/compare queries
- **Domain Routing** — Supplements, SARMs, Steroids, Peptides, Exercise, Nutrition

### Knowledge Base
- **19 Compound Profiles** — Creatine, Whey, Beta-alanine, Caffeine, Citrulline, Ostarine, LGD-4033, RAD-140, MK-677, Testosterone, Anavar, Nandrolone, BPC-157, HGH, Vitamin D, Omega-3, ZMA, Fat Burners
- **8 General Topics** — Fat Loss Exercise, Muscle Gain Training, Beginner Workouts, HIIT/Cardio, Protein Diet, Fat Loss Diet, Natural Testosterone, Supplement Guide

### AI Pipeline
```
User Query
  ↓ Intent Classification (dosage/cycle/research/product/compare)
  ↓ Domain Detection (supplements/steroids/sarms/peptides/exercise/nutrition)
  ↓ Entity Extraction (specific compound?)
  ↓ Cache Check (24h SQLite cache)
  ↓ Knowledge Base Lookup (strict scoring for compounds / topic match for general)
  ↓ Live PubMed Retrieval (optional, requires network)
  ↓ Claude AI Enhancement (optional, requires ANTHROPIC_API_KEY)
  ↓ Structured 17-Section Report
  ↓ Return to Frontend
```

### Tools
- 🥗 **Diet Planner** — AI-generated meal plans with macros
- 🔬 **Cycle Planner** — Steroid/SARM cycle protocols
- 🏥 **Medical Screen** — Pre-cycle bloodwork analysis
- 📏 **Body Composition** — BCA analysis
- 💪 **Physique Tracker** — Progress photo upload
- 🛒 **Grocery AI** — Supplement shopping list

## 📁 Project Structure

```
ai-fitness-platform-main/
├── frontend/
│   ├── index.html          # Main AI Search Engine (REWRITTEN)
│   ├── login.html          # Auth - Sign In (REWRITTEN)
│   ├── register.html       # Auth - Register (REWRITTEN)
│   ├── dashboard.html      # User Dashboard (REWRITTEN)
│   ├── diet.html           # Diet Planner
│   ├── cycle.html          # Cycle Planner
│   ├── medical.html        # Medical Screen
│   ├── bca.html            # Body Composition
│   ├── physique.html       # Physique Tracker
│   └── grocery.html        # Grocery AI
├── backend/
│   ├── app.py              # Flask App - All Routes (REWRITTEN v6)
│   ├── search_ai.py        # Core Search Engine (KB + AI)
│   ├── diet_ai.py          # Diet Generation
│   ├── calorie_ai.py       # TDEE Calculator
│   ├── cycle_ai.py         # Cycle Planner
│   ├── medical_ai.py       # Medical Analysis
│   ├── supplement_ai.py    # Supplement Data
│   └── ...
├── database/
│   ├── users.db            # SQLite user database
│   └── search_cache.db     # Search result cache
├── uploads/                # User uploaded files
├── static/                 # Static assets
├── requirements.txt
├── render.yaml             # Render.com deployment
└── passenger_wsgi.py       # cPanel/Passenger deployment
```

## 🛠 Setup & Deployment

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export ANTHROPIC_API_KEY="your-claude-api-key"   # Optional but recommended
export PUBMED_API_KEY="your-pubmed-key"          # Optional
export SECRET_KEY="your-secret-key-change-this"

# 3. Run
python -m backend.app
# OR
flask --app backend.app run --port 5000

# Visit: http://localhost:5000
```

### Render.com (Recommended)

1. Push repo to GitHub
2. Create new Web Service on Render
3. Connect your repo
4. Set environment variables:
   - `ANTHROPIC_API_KEY` = your Claude API key
   - `SECRET_KEY` = random secure string (Render can generate)
   - `PUBMED_API_KEY` = optional
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### cPanel/Shared Hosting

Uses `passenger_wsgi.py` — configure Python app to point to this file.

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Optional | Claude AI for enhanced responses |
| `SECRET_KEY` | Recommended | Flask session secret (change in production!) |
| `PUBMED_API_KEY` | Optional | Faster PubMed API requests |
| `SERP_API_KEY` | Optional | Google search results |
| `PORT` | Optional | Server port (default: 5000) |

## 🔍 API Endpoints

### Auth
- `POST /register` — Create account
- `POST /login` — Sign in
- `POST /logout` — Sign out
- `GET /me` — Get current user
- `PUT /profile` — Update profile

### Search
- `POST /search` — Main AI search
- `GET /search/suggestions?q=...` — Autocomplete
- `GET /recommendations` — Personalized recs

### History
- `GET /history` — Search history
- `DELETE /history/clear` — Clear all
- `DELETE /history/:id` — Delete one

### Tools
- `POST /diet` — Generate diet plan
- `POST /cycle` — Generate cycle protocol
- `POST /medical` — Medical analysis
- `POST /upload_bca` — Upload body scan
- `POST /upload_medical` — Upload bloodwork
- `POST /upload_physique` — Upload progress photo

### System
- `GET /health` — Health check
- `GET /cache/stats` — Cache statistics
- `DELETE /cache/clear` — Clear cache

## 🔬 Query Examples

```
# Supplements
"What is creatine monohydrate?"
"Best pre-workout stack for strength"
"Whey protein vs casein comparison"

# SARMs
"RAD-140 dosage and cycle"
"Ostarine MK-2866 for beginners"
"LGD-4033 side effects"

# Steroids
"Testosterone enanthate beginner cycle"
"Anavar cutting protocol"
"PCT after steroid cycle"

# Peptides
"BPC-157 for tendon healing"
"Ipamorelin CJC-1295 stack"
"MK-677 ibutamoren dosage"

# Training
"Best exercises for fat loss women"
"Hypertrophy training program"
"HIIT vs steady state cardio"

# Nutrition
"High protein diet muscle gain"
"Calorie deficit for fat loss"
"Intermittent fasting guide"
```

## ⚠️ Medical Disclaimer

This platform is for **educational and informational purposes only**. It does not constitute medical advice. Always consult a qualified healthcare professional before starting any supplement, hormone, or performance-enhancing compound protocol. Performance-enhancing drugs carry significant health risks and may be illegal in your jurisdiction.

---

Built with ❤️ using Flask, Claude AI, PubMed API, and a comprehensive fitness knowledge base.
