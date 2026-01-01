"""
Database layer using Supabase for puzzle storage and authentication.
Falls back to local puzzles if Supabase is not configured.
"""
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import hashlib

from config import get_settings

# Try to import supabase, handle if not installed
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # type: ignore

# Cache for supabase client
_supabase_client: Any = None


def get_supabase_client() -> Any:
    """Get or create Supabase client."""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        return None
        
    settings = get_settings()
    if not settings.supabase_configured:
        return None
    
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    return _supabase_client


def get_supabase_admin_client() -> Any:
    """Get Supabase client with service role key for admin operations."""
    if not SUPABASE_AVAILABLE:
        return None
        
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        return None
    
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )


# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

async def sign_in_with_email(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Sign in a user with email and password using Supabase Auth.
    Returns (user_data, error_message).
    """
    client = get_supabase_client()
    if not client:
        # Fallback to simple password check if Supabase is not configured
        settings = get_settings()
        if password == settings.ADMIN_SECRET and settings.ADMIN_SECRET != "change-me-in-production":
            return {"email": email, "fallback": True}, None
        return None, "Invalid credentials"
    
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }, None
        return None, "Invalid credentials"
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return None, "Invalid email or password"
        return None, f"Authentication error: {error_msg}"


async def sign_out(access_token: str) -> bool:
    """Sign out a user."""
    client = get_supabase_client()
    if not client:
        return True
    
    try:
        client.auth.sign_out()
        return True
    except Exception:
        return True  # Consider signed out even if error


async def verify_session(access_token: str) -> Optional[Dict]:
    """
    Verify an access token and return user data if valid.
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.auth.get_user(access_token)
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email
            }
    except Exception:
        pass
    
    return None


async def refresh_session(refresh_token: str) -> Optional[Dict]:
    """
    Refresh an expired session using a refresh token.
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.auth.refresh_session(refresh_token)
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
    except Exception:
        pass
    
    return None


async def get_all_puzzles() -> List[Dict]:
    """Fetch all puzzles from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("puzzles").select("*").order("created_at", desc=True).execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching puzzles: {e}")
        return []


async def get_active_puzzles() -> List[Dict]:
    """Fetch only active puzzles from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("puzzles").select("*").eq("active", True).execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching active puzzles: {e}")
        return []


async def get_puzzle_by_date(date_str: str) -> Optional[Dict]:
    """Get a specific puzzle assigned to a date."""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table("puzzles").select("*").eq("scheduled_date", date_str).single().execute()
        return response.data
    except Exception:
        return None


async def add_puzzle(puzzle: Dict) -> Optional[Dict]:
    """Add a new puzzle to Supabase."""
    client = get_supabase_admin_client()
    if not client:
        return None
    
    try:
        puzzle_data = {
            "sentence": puzzle["sentence"],
            "target": puzzle["target"],
            "pronunciation": puzzle["pronunciation"],
            "meaning": puzzle["meaning"],
            "example": puzzle.get("example", ""),
            "active": puzzle.get("active", True),
            "scheduled_date": puzzle.get("scheduled_date"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        response = client.table("puzzles").insert(puzzle_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding puzzle: {e}")
        return None


async def add_puzzles_bulk(puzzles: List[Dict]) -> List[Dict]:
    """Add multiple puzzles to Supabase."""
    client = get_supabase_admin_client()
    if not client:
        return []
    
    try:
        puzzle_data = []
        for puzzle in puzzles:
            puzzle_data.append({
                "sentence": puzzle["sentence"],
                "target": puzzle["target"],
                "pronunciation": puzzle["pronunciation"],
                "meaning": puzzle["meaning"],
                "example": puzzle.get("example", ""),
                "active": puzzle.get("active", True),
                "scheduled_date": puzzle.get("scheduled_date"),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        response = client.table("puzzles").insert(puzzle_data).execute()
        return response.data or []
    except Exception as e:
        error_msg = str(e)
        print(f"Error adding puzzles: {error_msg}")
        # Re-raise with more context
        if "duplicate" in error_msg.lower():
            raise ValueError(f"Duplicate puzzle detected: {error_msg}")
        raise ValueError(f"Database error: {error_msg}")


async def update_puzzle(puzzle_id: str, updates: Dict) -> Optional[Dict]:
    """Update an existing puzzle."""
    client = get_supabase_admin_client()
    if not client:
        return None
    
    try:
        response = client.table("puzzles").update(updates).eq("id", puzzle_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating puzzle: {e}")
        return None


async def delete_puzzle(puzzle_id: str) -> bool:
    """Delete a puzzle."""
    client = get_supabase_admin_client()
    if not client:
        return False
    
    try:
        client.table("puzzles").delete().eq("id", puzzle_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting puzzle: {e}")
        return False


async def schedule_puzzle(puzzle_id: str, date_str: str) -> Optional[Dict]:
    """Schedule a puzzle for a specific date."""
    client = get_supabase_admin_client()
    if not client:
        return None
    
    try:
        # First, unschedule any puzzle currently on that date
        client.table("puzzles").update({"scheduled_date": None}).eq("scheduled_date", date_str).execute()
        
        # Then schedule the new puzzle
        response = client.table("puzzles").update({"scheduled_date": date_str}).eq("id", puzzle_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error scheduling puzzle: {e}")
        return None


def get_daily_puzzle_index(puzzles_count: int, date_str: str) -> int:
    """
    Get the puzzle index for a given date.
    Uses a hash to ensure consistent puzzle selection.
    """
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    return hash_value % puzzles_count if puzzles_count > 0 else 0
