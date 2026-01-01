# kalimle 🔤

A daily Arabic word guessing game inspired by Wordle. Players guess Modern Standard Arabic (MSA) words to fill in English sentence blanks.

## Features

- **Daily Puzzle**: One word per day, same for all players worldwide
- **6 Guesses**: Players have 6 attempts to guess the correct Arabic word
- **Color Feedback**:
  - 🟩 **Green**: Correct letter in correct position
  - 🟨 **Yellow**: Correct letter in wrong position
  - ⬛ **Gray**: Letter not in the word
- **Share Results**: Share your score with emoji grid
- **Server-Side Rendering**: No SPA framework, just FastAPI + Jinja2 templates

## Tech Stack

- **Backend**: FastAPI (Python)
- **Templates**: Jinja2 (server-side HTML rendering)
- **Database**: Supabase (PostgreSQL) for puzzle storage
- **Styling**: Vanilla CSS (Wordle-inspired dark theme)
- **JavaScript**: Minimal vanilla JS (countdown timer, share functionality)
- **Deployment**: Railway-ready

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd kalimle
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

## Project Structure

```
kalimle/
├── main.py                 # FastAPI application
├── config.py               # Configuration management
├── database.py             # Supabase database layer
├── game/
│   ├── __init__.py
│   └── logic.py            # Game logic (puzzles, validation)
├── templates/
│   ├── game.html           # Main game template
│   ├── admin.html          # Admin panel template
│   └── admin_login.html    # Admin login template
├── static/
│   ├── css/
│   │   ├── style.css       # Wordle-style CSS
│   │   └── admin.css       # Admin panel CSS
│   └── js/
│       └── game.js         # Minimal JS (countdown, share)
├── supabase_setup.sql      # SQL to setup Supabase tables
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
├── Procfile                # Railway deployment
├── railway.json            # Railway configuration
└── README.md
```

## How It Works

1. **Daily Word Selection**: A hash of the current date selects from a pool of 30 puzzles, ensuring the same word globally each day
2. **Arabic Text Normalization**: Handles diacritics, alef variations, and other Arabic text nuances
3. **Server-Side State**: Game state is stored in HTTP cookies (no database required)
4. **Letter Matching**: Uses Wordle's algorithm - green for exact matches, yellow for present letters, gray for absent

## Deployment on Railway

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Add environment variables in Railway dashboard (see below)
4. Railway will auto-detect the Python project and deploy

### Required Environment Variables for Railway

| Variable | Description |
|----------|-------------|
| `ADMIN_SECRET` | Fallback password for admin access (used when Supabase not configured) |
| `SUPABASE_URL` | Your Supabase project URL (required for full features) |
| `SUPABASE_KEY` | Your Supabase anon/public key (required for full features) |

Or deploy manually:
```bash
railway up
```

## Supabase Setup (Recommended)

Supabase provides both **puzzle storage** and **admin authentication**:

1. **Create a Supabase project** at [supabase.com](https://supabase.com)

2. **Run the setup SQL** in Supabase SQL Editor:
   - Open `supabase_setup.sql` from this repository
   - Copy and paste into the Supabase SQL Editor
   - Execute to create the `puzzles` table

3. **Create admin user(s)**:
   - Go to Authentication → Users in Supabase Dashboard
   - Click "Add User" → "Create New User"
   - Enter email and password for admin access
   - These credentials will be used to login to the admin panel

4. **Get your credentials**:
   - Go to Project Settings → API
   - Copy the Project URL → `SUPABASE_URL`
   - Copy the `anon` public key → `SUPABASE_KEY`

5. **Add to Railway**:
   - Go to your Railway project → Variables
   - Add `SUPABASE_URL` and `SUPABASE_KEY`

## Admin Panel

Access the admin panel at `/admin` to:

- **Add single puzzles** with all required fields
- **Bulk import puzzles** from JSON
- **Schedule puzzles** for specific dates
- **Enable/disable puzzles**
- **Delete puzzles**
- **View today's puzzle** and database status

### Admin Authentication

**With Supabase configured:**
- Login using email/password credentials
- Create admin users in Supabase Dashboard → Authentication → Users
- Sessions are validated against Supabase Auth

**Without Supabase (fallback):**
- Login using the `ADMIN_SECRET` environment variable password

## Adding New Puzzles

### Via Admin Panel (Recommended)

1. Go to `/admin` and login with your credentials
2. Use the "Add Single Puzzle" form, or
3. Use "Bulk Add Puzzles" with JSON format:

```json
[
  {
    "sentence": "I am reading a ___.",
    "target": "كتاب",
    "pronunciation": "kitāb",
    "meaning": "book",
    "example": "أقرأ كتاباً ممتعاً"
  }
]
```

### Via Code (Fallback)

If Supabase is not configured, edit `game/logic.py` and add entries to `DAILY_PUZZLES`:

```python
{
    "sentence": "Your English sentence with ___.",
    "target": "عربي",
    "pronunciation": "ʿarabī",
    "meaning": "Arabic",
    "example": "مثال بالعربية"
}
```

## Daily Puzzle Selection

The puzzle changes at **midnight GMT** every day. The selection works as follows:

1. **Scheduled puzzles** take priority - if a puzzle is scheduled for a specific date, it will be shown
2. **Hash-based selection** - otherwise, a deterministic hash of the date selects from active puzzles
3. **Fallback puzzles** - if Supabase is not configured, local puzzles from `logic.py` are used

This ensures all players worldwide see the same puzzle on the same day.

## License

MIT License - feel free to use and modify!
