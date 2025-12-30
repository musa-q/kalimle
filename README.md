# Arabic Wordle 🔤

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
- **Styling**: Vanilla CSS (Wordle-inspired dark theme)
- **JavaScript**: Minimal vanilla JS (countdown timer, share functionality)
- **Deployment**: Railway-ready

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd arabic-wordle
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
arabic-wordle/
├── main.py                 # FastAPI application
├── game/
│   ├── __init__.py
│   └── logic.py            # Game logic (puzzles, validation)
├── templates/
│   └── game.html           # Jinja2 HTML template
├── static/
│   ├── css/
│   │   └── style.css       # Wordle-style CSS
│   └── js/
│       └── game.js         # Minimal JS (countdown, share)
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
3. Railway will auto-detect the Python project and deploy

Or deploy manually:
```bash
railway up
```

## Adding New Puzzles

Edit `game/logic.py` and add entries to `DAILY_PUZZLES`:

```python
{
    "sentence": "Your English sentence with ___.",
    "target": "عربي",
    "pronunciation": "ʿarabī",
    "meaning": "Arabic",
    "example": "مثال بالعربية"
}
```

## License

MIT License - feel free to use and modify!
