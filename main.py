"""
kalimle - FastAPI Application
Server-side rendered game with minimal JavaScript.
"""
from fastapi import FastAPI, Request, Form, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import os
import hashlib
import secrets

from game.logic import (
    get_todays_puzzle,
    validate_guess,
    validate_guess_length,
    check_win,
    get_game_state_key,
    get_today_gmt,
    MAX_GUESSES,
    normalize_arabic,
    count_arabic_letters
)
from config import get_settings
import database

app = FastAPI(title="kalimle", description="Daily Arabic Word Puzzle Game")

# Setup templates and static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# Admin session management - stores access tokens
# In production with multiple instances, use Redis or database
ADMIN_SESSIONS = {}


async def verify_admin_session(
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
) -> Optional[dict]:
    """
    Check if the admin session is valid.
    Returns user data if valid, None otherwise.
    """
    if not admin_session:
        return None
    
    # Check local session cache first
    if admin_session not in ADMIN_SESSIONS:
        return None
    
    session_data = ADMIN_SESSIONS[admin_session]
    
    # If using Supabase auth, verify the token is still valid
    if admin_token and not session_data.get("fallback"):
        user = await database.verify_session(admin_token)
        if not user:
            # Try to refresh the session
            refresh_token = session_data.get("refresh_token")
            if refresh_token:
                new_session = await database.refresh_session(refresh_token)
                if new_session:
                    session_data["access_token"] = new_session["access_token"]
                    session_data["refresh_token"] = new_session["refresh_token"]
                    return session_data
            # Session expired, remove it
            del ADMIN_SESSIONS[admin_session]
            return None
    
    return session_data


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


@app.post("/api/guess")
async def api_submit_guess(
    request: Request,
    guess: str = Form(...),
    game_state: Optional[str] = Cookie(default=None)
):
    """JSON API endpoint for guess submission."""
    puzzle = get_todays_puzzle()
    state = get_game_state(game_state)
    
    # Don't process if game is already over
    if state["game_over"]:
        return JSONResponse({"error": "Game already over"}, status_code=400)
    
    # Clean and validate the guess
    guess = guess.strip()
    
    # Validate guess length
    is_valid, error_msg = validate_guess_length(guess, puzzle["target"])
    if not is_valid:
        return JSONResponse({"error": error_msg}, status_code=400)
    
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
    
    # Prepare response data
    response_data = {
        "success": True,
        "guess": guess,
        "feedback": feedback,
        "game_over": state["game_over"],
        "won": state["won"],
        "remaining_guesses": MAX_GUESSES - len(state["guesses"]),
        "target": puzzle["target"] if state["game_over"] else None,
        "pronunciation": puzzle["pronunciation"] if state["game_over"] else None,
        "meaning": puzzle["meaning"] if state["game_over"] else None,
        "example": puzzle["example"] if state["game_over"] else None
    }
    
    # Create response with updated cookie
    response = JSONResponse(response_data)
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


# =============================================================================
# ADMIN ROUTES
# =============================================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None),
    success: Optional[str] = None,
    error: Optional[str] = None
):
    """Admin panel page."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    settings = get_settings()
    puzzles = await database.get_all_puzzles()
    today_puzzle = get_todays_puzzle()
    today_date = get_today_gmt().isoformat()
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "puzzles": puzzles,
        "today_puzzle": today_puzzle,
        "today_date": today_date,
        "supabase_configured": settings.supabase_configured,
        "user_email": user.get("email", "Admin"),
        "success": success,
        "error": error
    })


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(
    request: Request, 
    error: Optional[str] = None,
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Admin login page."""
    # Redirect to admin if already logged in
    user = await verify_admin_session(admin_session, admin_token)
    if user:
        return RedirectResponse(url="/admin", status_code=303)
    
    settings = get_settings()
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": error,
        "supabase_configured": settings.supabase_configured
    })


@app.post("/admin/login")
async def admin_login(
    request: Request, 
    email: str = Form(""),
    password: str = Form(...)
):
    """Process admin login with Supabase Auth."""
    settings = get_settings()
    
    # Try Supabase Auth first if configured
    if settings.supabase_configured and email:
        user_data, error = await database.sign_in_with_email(email, password)
        
        if user_data:
            # Create session token
            session_token = secrets.token_urlsafe(32)
            ADMIN_SESSIONS[session_token] = user_data
            
            response = RedirectResponse(url="/admin", status_code=303)
            response.set_cookie(
                key="admin_session",
                value=session_token,
                max_age=86400 * 7,  # 7 days
                httponly=True,
                samesite="lax"
            )
            # Also store access token for session verification
            if user_data.get("access_token"):
                response.set_cookie(
                    key="admin_token",
                    value=user_data["access_token"],
                    max_age=86400 * 7,
                    httponly=True,
                    samesite="lax"
                )
            return response
        
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": error or "Invalid credentials",
            "supabase_configured": True
        })
    
    # Fallback to simple password check if Supabase not configured
    if secrets.compare_digest(password, settings.ADMIN_SECRET):
        session_token = secrets.token_urlsafe(32)
        ADMIN_SESSIONS[session_token] = {"email": "admin", "fallback": True}
        
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=session_token,
            max_age=86400,  # 24 hours
            httponly=True,
            samesite="lax"
        )
        return response
    
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Invalid password",
        "supabase_configured": False
    })


@app.post("/admin/logout")
async def admin_logout(
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Process admin logout."""
    if admin_session and admin_session in ADMIN_SESSIONS:
        # Sign out from Supabase if applicable
        if admin_token:
            await database.sign_out(admin_token)
        del ADMIN_SESSIONS[admin_session]
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("admin_session")
    response.delete_cookie("admin_token")
    return response


@app.post("/admin/puzzle/add")
async def add_puzzle(
    request: Request,
    sentence: str = Form(...),
    target: str = Form(...),
    pronunciation: str = Form(...),
    meaning: str = Form(...),
    example: str = Form(""),
    scheduled_date: Optional[str] = Form(None),
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Add a single puzzle."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    puzzle = {
        "sentence": sentence.strip(),
        "target": target.strip(),
        "pronunciation": pronunciation.strip(),
        "meaning": meaning.strip(),
        "example": example.strip(),
        "scheduled_date": scheduled_date if scheduled_date else None
    }
    
    result = await database.add_puzzle(puzzle)
    
    if result:
        return RedirectResponse(url="/admin?success=Puzzle added successfully!", status_code=303)
    else:
        return RedirectResponse(url="/admin?error=Failed to add puzzle. Check Supabase configuration.", status_code=303)


@app.post("/admin/puzzle/bulk-add")
async def bulk_add_puzzles(
    request: Request,
    bulk_puzzles: str = Form(...),
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Add multiple puzzles from JSON."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    try:
        puzzles = json.loads(bulk_puzzles)
        if not isinstance(puzzles, list):
            raise ValueError("Expected a JSON array")
        
        # Validate each puzzle has required fields
        required_fields = ["sentence", "target", "pronunciation", "meaning"]
        for i, puzzle in enumerate(puzzles):
            missing = [f for f in required_fields if f not in puzzle]
            if missing:
                raise ValueError(f"Puzzle {i+1} is missing: {', '.join(missing)}")
        
        results = await database.add_puzzles_bulk(puzzles)
        
        if results:
            return RedirectResponse(
                url=f"/admin?success=Successfully added {len(results)} puzzles!", 
                status_code=303
            )
        else:
            return RedirectResponse(
                url="/admin?error=Failed to add puzzles. Check Supabase configuration.", 
                status_code=303
            )
    except json.JSONDecodeError:
        return RedirectResponse(url="/admin?error=Invalid JSON format", status_code=303)
    except ValueError as e:
        error_msg = str(e).replace("'", "").replace('"', '')  # Clean quotes for URL
        return RedirectResponse(url=f"/admin?error={error_msg}", status_code=303)
    except Exception as e:
        error_msg = str(e).replace("'", "").replace('"', '')  # Clean quotes for URL
        return RedirectResponse(url=f"/admin?error=Unexpected error: {error_msg}", status_code=303)


@app.post("/admin/puzzle/toggle/{puzzle_id}")
async def toggle_puzzle(
    puzzle_id: str,
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Toggle puzzle active status."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    # Get current puzzle state
    puzzles = await database.get_all_puzzles()
    puzzle = next((p for p in puzzles if p["id"] == puzzle_id), None)
    
    if puzzle:
        new_status = not puzzle.get("active", True)
        await database.update_puzzle(puzzle_id, {"active": new_status})
        return RedirectResponse(url="/admin?success=Puzzle status updated!", status_code=303)
    
    return RedirectResponse(url="/admin?error=Puzzle not found", status_code=303)


@app.post("/admin/puzzle/delete/{puzzle_id}")
async def delete_puzzle(
    puzzle_id: str,
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Delete a puzzle."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    success = await database.delete_puzzle(puzzle_id)
    
    if success:
        return RedirectResponse(url="/admin?success=Puzzle deleted!", status_code=303)
    return RedirectResponse(url="/admin?error=Failed to delete puzzle", status_code=303)


@app.post("/admin/puzzle/schedule")
async def schedule_puzzle(
    puzzle_id: str = Form(...),
    date: str = Form(...),
    admin_session: Optional[str] = Cookie(default=None),
    admin_token: Optional[str] = Cookie(default=None)
):
    """Schedule a puzzle for a specific date."""
    user = await verify_admin_session(admin_session, admin_token)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    result = await database.schedule_puzzle(puzzle_id, date)
    
    if result:
        return RedirectResponse(url=f"/admin?success=Puzzle scheduled for {date}!", status_code=303)
    return RedirectResponse(url="/admin?error=Failed to schedule puzzle", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
