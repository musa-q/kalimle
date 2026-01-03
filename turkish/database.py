"""
Database layer for Turkish kelimle app.
Uses the shared database module with Turkish-specific configuration.
"""
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
import asyncio

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.base import BaseDatabase
from shared.game.logic import get_puzzle_index_for_date, get_today_gmt
from turkish.config import get_settings
from turkish.language_config import FALLBACK_PUZZLES


# Singleton database instance
_db_instance: Optional[BaseDatabase] = None


def get_database() -> BaseDatabase:
    """Get or create database instance."""
    global _db_instance
    
    if _db_instance is None:
        settings = get_settings()
        _db_instance = BaseDatabase(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY,
            supabase_service_key=settings.SUPABASE_SERVICE_KEY,
            admin_secret=settings.ADMIN_SECRET
        )
    
    return _db_instance


# Cache for puzzles
_cached_puzzles: List[Dict] = []
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutes


# ============================================================================
# AUTHENTICATION - Delegate to shared database
# ============================================================================

async def sign_in_with_email(email: str, password: str):
    """Sign in with email and password."""
    return await get_database().sign_in_with_email(email, password)


async def sign_out(access_token: str) -> bool:
    """Sign out a user."""
    return await get_database().sign_out(access_token)


async def verify_session(access_token: str):
    """Verify session token."""
    return await get_database().verify_session(access_token)


async def refresh_session(refresh_token: str):
    """Refresh session."""
    return await get_database().refresh_session(refresh_token)


# ============================================================================
# PUZZLE OPERATIONS
# ============================================================================

async def get_all_puzzles() -> List[Dict]:
    """Fetch all puzzles."""
    return await get_database().get_all_puzzles()


async def get_active_puzzles() -> List[Dict]:
    """Fetch active puzzles."""
    global _cached_puzzles, _cache_timestamp
    
    now = datetime.now(timezone.utc)
    
    # Check if cache is still valid
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
        if _cached_puzzles:
            return _cached_puzzles
    
    puzzles = await get_database().get_active_puzzles()
    if puzzles:
        _cached_puzzles = puzzles
        _cache_timestamp = now
    
    return puzzles


async def add_puzzle(puzzle: Dict):
    """Add a puzzle."""
    return await get_database().add_puzzle(puzzle)


async def add_puzzles_bulk(puzzles: List[Dict]):
    """Add multiple puzzles."""
    return await get_database().add_puzzles_bulk(puzzles)


async def update_puzzle(puzzle_id: str, updates: Dict):
    """Update a puzzle."""
    return await get_database().update_puzzle(puzzle_id, updates)


async def delete_puzzle(puzzle_id: str) -> bool:
    """Delete a puzzle."""
    return await get_database().delete_puzzle(puzzle_id)


async def schedule_puzzle(puzzle_id: str, date_str: str):
    """Schedule a puzzle for a date."""
    return await get_database().schedule_puzzle(puzzle_id, date_str)


# ============================================================================
# TODAY'S PUZZLE
# ============================================================================

def _fetch_puzzles_sync() -> List[Dict]:
    """Synchronous wrapper to fetch puzzles from database."""
    global _cached_puzzles, _cache_timestamp
    
    now = datetime.now(timezone.utc)
    
    # Check if cache is still valid
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
        if _cached_puzzles:
            return _cached_puzzles
    
    # Try to fetch from database
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context - just use cache or fallback
            return _cached_puzzles if _cached_puzzles else []
        except RuntimeError:
            # No running loop - we can create one
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                puzzles = loop.run_until_complete(get_active_puzzles())
                if puzzles:
                    _cached_puzzles = puzzles
                    _cache_timestamp = now
                    return puzzles
            finally:
                loop.close()
    except Exception as e:
        print(f"Error fetching puzzles from database: {e}")
    
    return []


def get_todays_puzzle() -> Dict:
    """
    Get today's puzzle.
    Uses GMT timezone to ensure consistent puzzle for all users.
    Tries to fetch from database first, falls back to local puzzles.
    """
    today = get_today_gmt()
    date_str = today.isoformat()
    
    # Try to get puzzles from database
    try:
        puzzles = _fetch_puzzles_sync()
        if puzzles:
            # First check for scheduled puzzle
            for puzzle in puzzles:
                if puzzle.get("scheduled_date") == date_str:
                    return puzzle
            
            # Use hash-based selection
            index = get_puzzle_index_for_date(len(puzzles), today)
            return puzzles[index]
    except Exception as e:
        print(f"Error in get_todays_puzzle: {e}")
    
    # Fallback to local puzzles
    index = get_puzzle_index_for_date(len(FALLBACK_PUZZLES), today)
    return FALLBACK_PUZZLES[index]
