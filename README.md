# FitSearch AI Platform v4

AI-powered fitness and performance search engine with 6 core features.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialise the database (first run only)
python init_db.py

# 3. Run the development server
cd backend
python app.py
```

Open `frontend/index.html` in your browser, or serve via Flask's static files.

---

## Project structure

```
AI_Platform/
├── backend/
│   ├── app.py            — Flask API (all routes)
│   ├── search_ai.py      — Knowledge base search + recommendations
│   ├── supplement_ai.py  — Supplement comparison engine
│   ├── calorie_ai.py     — Calorie & TDEE calculator (Mifflin-St Jeor)
│   ├── diet_ai.py        — Full meal plan generator
│   ├── cycle_ai.py       — Cycle planner with PCT & bloodwork schedule
│   ├── medical_ai.py     — Basic medical risk screening
│   └── grocery_ai.py     — Weekly grocery list generator
├── frontend/
│   └── index.html        — Complete single-page application (SPA)
├── database/
│   └── users.db          — SQLite database
├── init_db.py            — Database initialisation script
├── passenger_wsgi.py     — WSGI entry point for shared hosting
└── requirements.txt
```

---

## Features

### 1. Login & registration
- Email + password authentication with SHA-256 hashing
- Session-based auth (cookie)
- Profile: name, goal, experience level, weight, height, age

### 2. Search with history
- `POST /search` — searches the knowledge base, logs query
- `GET /history` — returns last 50 searches
- `DELETE /history/clear` — clears all history
- Re-run any past query in one click

### 3. Personalised recommendations
- `GET /recommendations` — generates picks from recent search history
- Filtered by user goal + experience level
- Cold-start defaults for new users

### 4. Supplement comparison
- `POST /compare` — compare 2–4 compounds side by side
- Table with winner highlighting per attribute
- AI verdict based on user profile
- Quick-pick presets

### 5. Diet generator
- `POST /diet` — Mifflin-St Jeor TDEE + macro targets
- Full 6-meal plan with calories and macros per meal
- Supports muscle gain / fat loss / recomp goals
- Supplement stack included

### 6. Cycle planner
- `POST /cycle` — generates protocol from experience + category + goal
- Week-by-week schedule with phase colour coding
- On-cycle support compounds listed
- Bloodwork checkpoints
- Full safety disclaimer

---

## API reference (all routes require login except /register and /login)

| Method | Route | Description |
|--------|-------|-------------|
| POST | /register | Create account |
| POST | /login | Sign in |
| POST | /logout | Sign out |
| GET | /me | Current user profile |
| PUT | /profile | Update profile |
| POST | /search | Search knowledge base |
| GET | /history | Search history |
| DELETE | /history/clear | Clear all history |
| GET | /recommendations | Personalised recs |
| POST | /compare | Compare compounds |
| POST | /diet | Generate diet plan |
| POST | /cycle | Generate cycle plan |
| POST | /grocery | Weekly grocery list |
| POST | /medical | Medical risk screen |
| POST | /upload_bca | Upload BCA file |
| POST | /upload_physique | Upload physique photos |

---

## Upgrading to production

- Replace `app.secret_key` with a random 32-byte secret from env var
- Replace SQLite with PostgreSQL (`psycopg2`)
- Replace `hash_password` (SHA-256) with `bcrypt` or `argon2`
- Replace `search_ai.py` keyword scorer with Pinecone/Weaviate vector search
- Replace AI module stubs with real LLM calls (OpenAI / Anthropic API)
- Add rate limiting (`flask-limiter`)
- Serve frontend via Nginx, not Flask dev server
