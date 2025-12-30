"""
kalimle - FastAPI Application
Server-side rendered game with minimal JavaScript.
"""
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import os

from game.logic import (
    get_todays_puzzle,
    validate_guess,
    validate_guess_length,
    check_win,
    get_game_state_key,
    MAX_GUESSES,
    normalize_arabic,
    count_arabic_letters
)

app = FastAPI(title="kalimle", description="Daily Arabic Word Puzzle Game")

# Setup templates and static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


def get_game_state(game_state_cookie: Optional[str]) -> dict:
    """Parse game state from cookie or return fresh state."""
    today_key = get_game_state_key()
    
    if game_state_cookie:
        try:
            state = json.loads(game_state_cookie)
            # Check if this is today's game state
            if state.get("date") == today_key:
                return state
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Return fresh state for new day or invalid cookie
    return {
        "date": today_key,
        "guesses": [],
        "feedback": [],
        "game_over": False,
        "won": False
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, game_state: Optional[str] = Cookie(default=None)):
    """Main game page."""
    puzzle = get_todays_puzzle()
    state = get_game_state(game_state)
    
    return templates.TemplateResponse("game.html", {
        "request": request,
        "sentence": puzzle["sentence"],
        "guesses": state["guesses"],
        "feedback": state["feedback"],
        "game_over": state["game_over"],
        "won": state["won"],
        "max_guesses": MAX_GUESSES,
        "remaining_guesses": MAX_GUESSES - len(state["guesses"]),
        "target": puzzle["target"] if state["game_over"] else None,
        "pronunciation": puzzle["pronunciation"] if state["game_over"] else None,
        "meaning": puzzle["meaning"] if state["game_over"] else None,
        "example": puzzle["example"] if state["game_over"] else None,
        "target_length": count_arabic_letters(puzzle["target"])
    })


@app.post("/guess", response_class=HTMLResponse)
async def submit_guess(
    request: Request,
    guess: str = Form(...),
    game_state: Optional[str] = Cookie(default=None)
):
    """Process a guess submission."""
    puzzle = get_todays_puzzle()
    state = get_game_state(game_state)
    
    # Don't process if game is already over
    if state["game_over"]:
        response = RedirectResponse(url="/", status_code=303)
        return response
    
    # Clean and validate the guess
    guess = guess.strip()
    
    # Validate guess length
    is_valid, error_msg = validate_guess_length(guess, puzzle["target"])
    if not is_valid:
        return templates.TemplateResponse("game.html", {
            "request": request,
            "sentence": puzzle["sentence"],
            "guesses": state["guesses"],
            "feedback": state["feedback"],
            "game_over": state["game_over"],
            "won": state["won"],
            "max_guesses": MAX_GUESSES,
            "remaining_guesses": MAX_GUESSES - len(state["guesses"]),
            "target": None,
            "pronunciation": None,
            "meaning": None,
            "example": None,
            "target_length": count_arabic_letters(puzzle["target"]),
            "error": error_msg
        })
    
    # Get feedback for this guess
    feedback = validate_guess(guess, puzzle["target"])
    
    # Update state
    state["guesses"].append(guess)
    state["feedback"].append(feedback)
    
    # Check win/lose conditions
    if check_win(guess, puzzle["target"]):
        state["won"] = True
        state["game_over"] = True
    elif len(state["guesses"]) >= MAX_GUESSES:
        state["game_over"] = True
    
    # Create response with updated cookie
    response = templates.TemplateResponse("game.html", {
        "request": request,
        "sentence": puzzle["sentence"],
        "guesses": state["guesses"],
        "feedback": state["feedback"],
        "game_over": state["game_over"],
        "won": state["won"],
        "max_guesses": MAX_GUESSES,
        "remaining_guesses": MAX_GUESSES - len(state["guesses"]),
        "target": puzzle["target"] if state["game_over"] else None,
        "pronunciation": puzzle["pronunciation"] if state["game_over"] else None,
        "meaning": puzzle["meaning"] if state["game_over"] else None,
        "example": puzzle["example"] if state["game_over"] else None,
        "target_length": count_arabic_letters(puzzle["target"])
    })
    
    # Save state to cookie
    response.set_cookie(
        key="game_state",
        value=json.dumps(state),
        max_age=86400,  # 24 hours
        httponly=True,
        samesite="lax"
    )
    
    return response


@app.post("/reset", response_class=HTMLResponse)
async def reset_game():
    """Reset the game (clears cookie, but same puzzle remains for the day)."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("game_state")
    return response


@app.get("/api/puzzle", response_class=HTMLResponse)
async def get_puzzle_info():
    """API endpoint to get current puzzle info (for debugging)."""
    puzzle = get_todays_puzzle()
    return f"""
    <h2>Today's Puzzle</h2>
    <p><strong>Sentence:</strong> {puzzle["sentence"]}</p>
    <p><strong>Target:</strong> {puzzle["target"]}</p>
    <p><strong>Meaning:</strong> {puzzle["meaning"]}</p>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
