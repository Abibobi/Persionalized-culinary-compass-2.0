# 🍽️ Personalized Culinary Compass 2.0

> A full-stack, AI-assisted nutrition recommendation platform with hybrid search, safety-aware personalization, and automated meal planning.

[![CI](https://github.com/yourusername/Persionalized-culinary-compass-2.0/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/Persionalized-culinary-compass-2.0/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.x](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (:3000)                      │
│   Dashboard · Chatbot · Meal Planner · Onboarding · Saved Recipes │
└──────────────┬───────────────────────────────────┬───────────────┘
               │  REST API (JWT Auth)              │
┌──────────────▼───────────────────────────────────▼───────────────┐
│                     Django Backend (:8000)                         │
│  ┌──────────┐ ┌───────────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │
│  │ Accounts │ │Recommendations│ │ Safety │ │Planner │ │  API  │ │
│  │  Auth    │ │  Normalizer   │ │ Rules  │ │  Day   │ │ Views │ │
│  │  Profile │ │  Parser       │ │ Engine │ │ Planner│ │ Docs  │ │
│  │  Onboard │ │  Ranking      │ │ Alerts │ │ Regen  │ │       │ │
│  └──────────┘ │  Explanations │ └────────┘ │ Shop   │ └───────┘ │
│               │  Gemini AI    │            │ List   │           │
│               └───────────────┘            └────────┘           │
├──────────────────────────────────────────────────────────────────┤
│  PostgreSQL 16          Redis 7           Celery Worker          │
│  (recipes, profiles,    (task broker,     (async meal plan       │
│   interactions, plans)   result backend)   generation)           │
└──────────────────────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Hybrid Search** | Typo-tolerant NLP pipeline: normalizer → parser → fuzzy + semantic ranking |
| 🧠 **Smart Ranking** | 5-signal scoring: semantic match (35%), ingredient match (25%), profile fit (20%), nutrition goals (10%), popularity (10%) |
| 🛡️ **Safety Engine** | Allergy blocking, condition-aware warnings (diabetic, hypertension), diet integrity enforcement |
| 📋 **Meal Planner** | Full-day meal plans with calorie budgets, workout/low-carb modes, single-meal regeneration |
| 🤖 **AI Fallback** | Gemini-powered recipe suggestions when database search returns no results |
| 🛒 **Shopping List** | Auto-generated consolidated ingredient lists from meal plans |
| 💬 **Explanations** | Every recommendation includes "why this recipe" reasoning |
| 👤 **Personalization** | Diet type, allergies, health conditions, macro targets, cooking time, spice tolerance |

---

## 🚀 Quick Start

### Option A: Local Development (Recommended)

```bash
# 1. Clone and enter project
git clone https://github.com/yourusername/Persionalized-culinary-compass-2.0.git
cd Persionalized-culinary-compass-2.0

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Start database services
docker-compose up -d db redis

# 5. Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 6. Initialize database
python manage.py migrate
python manage.py seed_all

# 7. Run the backend
python manage.py runserver

# 8. (Optional) Start frontend
cd frontend && npm install && npm run dev
```

### Option B: Full Docker Stack

```bash
docker-compose up --build
```
This auto-runs migrations, seeds data, and starts the app on port 8000.

### Option C: PowerShell Portfolio Script (Windows)

```powershell
.\start_portfolio.ps1
```

---

## 🧪 Running Tests

```bash
# Full test suite (37 tests across all sprints)
python manage.py test tests.test_full_project --verbosity=2

# Individual app tests
python manage.py test recommendations.tests --verbosity=2
python manage.py test recipes.tests --verbosity=2

# With pytest
pytest
```

---

## 📊 API Documentation

Interactive API docs are available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/signup/` | Register new user |
| `POST` | `/api/v1/auth/login/` | Login (username or email) |
| `GET/PUT` | `/api/v1/users/me/profile/` | Get/update user profile |
| `POST` | `/api/v1/search/` | Hybrid recipe search |
| `GET` | `/api/v1/recipes/{id}/` | Recipe detail |
| `POST` | `/api/v1/recipes/{id}/save/` | Save recipe |
| `POST` | `/api/v1/recipes/{id}/feedback/` | Rate/review recipe |
| `GET` | `/api/v1/warnings/check/{id}/` | Safety check for recipe |
| `POST` | `/api/v1/meal-plans/generate/` | Generate day meal plan |
| `GET` | `/api/v1/meal-plans/{date}/` | Get plan by date |
| `PATCH` | `/api/v1/meal-plans/{id}/items/{item_id}/regenerate/` | Regenerate single meal |
| `GET` | `/api/v1/meal-plans/{id}/shopping-list/` | Shopping list for plan |

---

## 👥 Demo Users

| Username | Password | Profile |
|----------|----------|---------|
| `demo_vegan` | `demo1234!` | Vegan, allergic to peanuts & soy, 1800 cal target |
| `demo_diabetic` | `demo1234!` | Omnivore, diabetic, allergic to shellfish, 2000 cal target |
| `demo_athlete` | `demo1234!` | Omnivore, no restrictions, 3000 cal target, high protein |

---

## 📈 Case Study: Before → After

| Metric | v1.0 (Original) | v2.0 (Current) |
|--------|:---:|:---:|
| Query typo tolerance | ❌ None | ✅ Fuzzy + typo map |
| Personalized ranking | ❌ None | ✅ 5-signal weighted scoring |
| Safety warnings | ❌ None | ✅ Allergy + condition + diet rules |
| Meal planning | ❌ None | ✅ Full-day plans with regeneration |
| API documentation | ❌ None | ✅ OpenAPI 3.0 (Swagger + ReDoc) |
| Test coverage | ❌ 0 tests | ✅ 37+ integration & unit tests |
| Deployment | ❌ Manual | ✅ Docker + CI/CD pipeline |
| Auth system | Cookie-based sessions | JWT tokens + session fallback |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.x, Django REST Framework |
| **Auth** | JWT (SimpleJWT), django-allauth |
| **Database** | PostgreSQL 16, SQLite (dev fallback) |
| **Cache/Queue** | Redis 7, Celery |
| **NLP** | spaCy, RapidFuzz |
| **AI** | Google Gemini (fallback suggestions) |
| **Frontend** | Next.js (React) |
| **API Docs** | drf-spectacular (OpenAPI 3.0) |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker, Docker Compose |

---

## 📁 Project Structure

```
Persionalized-culinary-compass-2.0/
├── accounts/              # User auth, profile, onboarding
│   ├── management/commands/
│   │   ├── seed_all.py         # Master seed command
│   │   └── seed_demo_users.py  # Demo user profiles
│   ├── models.py          # UserProfile, UserRecipeInteraction
│   ├── auth_views.py      # Signup, login, logout
│   └── views.py           # Profile, dashboard, saved recipes
│
├── recommendations/       # Search & ranking engine
│   ├── services/
│   │   ├── normalizer.py       # Typo correction + fuzzy matching
│   │   ├── parser.py           # Entity extraction (diet, time, etc.)
│   │   ├── ranking.py          # 5-signal ranking formula
│   │   ├── explanations.py     # "Why this recipe" builder
│   │   └── gemini_fallback.py  # AI-powered suggestions
│   └── views.py           # Search API endpoint
│
├── safety/                # Health safety engine
│   ├── management/commands/
│   │   └── seed_safety_rules.py
│   ├── models.py          # SafetyRule (configurable via admin)
│   ├── services/
│   │   └── rules_engine.py     # Allergy, condition, diet checks
│   └── views.py           # Warning check endpoints
│
├── planner/               # Meal planning system
│   ├── models.py          # MealPlan, MealPlanItem
│   ├── services/
│   │   └── day_planner.py      # Plan generation algorithm
│   └── views.py           # Generate, get, regenerate, shopping list
│
├── recipes/               # Core recipe data
│   ├── models.py          # Recipe model
│   └── views.py           # Legacy + chatbot endpoints
│
├── api/                   # API gateway layer
│   ├── urls.py            # Route aggregation
│   └── views.py           # Health check, recipe CRUD
│
├── frontend/              # Next.js React frontend
├── tests/                 # Comprehensive test suite
├── .github/workflows/     # CI pipeline
├── docker-compose.yml     # Full stack orchestration
├── Dockerfile             # Production container
└── requirements.txt       # Python dependencies
```

---

## 🔒 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=pcc
DJANGO_DB_USER=postgres
DJANGO_DB_PASSWORD=postgres
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Optional: Gemini API key for AI fallback
GEMINI_API_KEY=your-gemini-api-key
```

---

## 📜 License

This project is built for portfolio and educational purposes.
