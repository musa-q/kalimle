# Multi-Language Wordle

A multi-language daily word puzzle game built with FastAPI. Currently supports Arabic (kalimle) and Turkish (kelimle) versions.

## Project Structure

```
wordle-multilang/
├── shared/                    # Shared code across all languages
│   ├── game/
│   │   ├── __init__.py
│   │   └── logic.py          # Base game logic (validation, win checking)
│   ├── database/
│   │   ├── __init__.py
│   │   └── base.py           # Base database operations
│   ├── templates/
│   │   ├── base_game.html    # Base game template
│   │   └── base_admin.html   # Base admin template
│   └── static/
│       ├── css/
│       │   ├── base.css      # Shared game styles
│       │   └── admin.css     # Shared admin styles
│       └── js/
│           └── game.js       # Shared game JavaScript
│
├── arabic/                    # Arabic version (kalimle)
│   ├── main.py               # FastAPI application
│   ├── config.py             # Environment configuration
│   ├── database.py           # Arabic database wrapper
│   ├── language_config.py    # Arabic-specific settings
│   ├── templates/
│   │   ├── game.html
│   │   ├── admin.html
│   │   └── admin_login.html
│   ├── static/css/style.css  # Arabic-specific styles
│   ├── .env.example
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.json
│
└── turkish/                   # Turkish version (kelimle)
    ├── main.py               # FastAPI application
    ├── config.py             # Environment configuration
    ├── database.py           # Turkish database wrapper
    ├── language_config.py    # Turkish-specific settings
    ├── templates/
    │   ├── game.html
    │   ├── admin.html
    │   └── admin_login.html
    ├── static/css/style.css  # Turkish-specific styles
    ├── .env.example
    ├── requirements.txt
    ├── Procfile
    └── railway.json
```

## Features

- **Shared Game Logic**: Core Wordle algorithm shared across all languages
- **Language-Specific Normalization**: Each language handles character equivalences differently
  - Arabic: Normalizes alif variations, removes diacritics
  - Turkish: Handles İ/I and ı/i distinctions
- **Independent Deployments**: Each language is a separate Railway project with its own database
- **Admin Panel**: Manage word lists, schedule puzzles, bulk import

## Local Development

### Running Arabic Version

```bash
cd arabic
cp .env.example .env
# Edit .env with your Supabase credentials
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Running Turkish Version

```bash
cd turkish
cp .env.example .env
# Edit .env with your Supabase credentials
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Deployment on Railway

### Option 1: Two Services from One Repo (Recommended)

1. Create a new Railway project
2. Connect to this GitHub repository
3. Create two services:
   - **kalimle-arabic**: Set root directory to `/arabic`
   - **kelimle-turkish**: Set root directory to `/turkish`
4. Add environment variables to each service:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `ADMIN_SECRET`

### Option 2: Separate Railway Projects

1. Create two Railway projects
2. Both connect to the same repo
3. Configure each with different root directories and env vars

## Adding a New Language

1. Copy the `turkish/` folder as a template
2. Rename to your language code (e.g., `spanish/`)
3. Update `language_config.py`:
   - Set `LANGUAGE_CODE`, `LANGUAGE_NAME`, `APP_NAME`
   - Define the keyboard layout
   - Implement `normalize_text()` for language-specific rules
   - Add fallback puzzles
4. Create a new Supabase project for the language
5. Deploy as a new Railway service

## Database Schema

Each language uses the same Supabase schema (in separate projects):

```sql
CREATE TABLE puzzles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sentence TEXT NOT NULL,
    target TEXT NOT NULL,
    pronunciation TEXT NOT NULL,
    meaning TEXT NOT NULL,
    example TEXT DEFAULT '',
    active BOOLEAN DEFAULT true,
    scheduled_date DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_puzzles_active ON puzzles(active);
CREATE INDEX idx_puzzles_scheduled ON puzzles(scheduled_date);
```

## Architecture Benefits

| Feature | Description |
|---------|-------------|
| **Shared Logic** | Bug fixes in `shared/game/logic.py` benefit all languages |
| **Independent Data** | Each language has its own Supabase database |
| **Independent Deploy** | Deploy Arabic without affecting Turkish |
| **Language Customization** | Each version can have unique styling, keyboard, and rules |
| **Easy Scaling** | Add new languages by copying the template |

## License

MIT
