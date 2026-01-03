"""
Shared Database Layer using Supabase.
Base class for puzzle storage and authentication that works across all language versions.
"""
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import hashlib


# Try to import supabase, handle if not installed
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # type: ignore


def get_supabase_client(url: str, key: str) -> Any:
    """
    Create a Supabase client.
    
    Args:
        url: Supabase project URL
        key: Supabase anon/public key
        
    Returns:
        Supabase client or None if not available
    """
    if not SUPABASE_AVAILABLE:
        return None
    
    if not url or not key:
        return None
    
    return create_client(url, key)


def get_supabase_admin_client(url: str, service_key: str) -> Any:
    """
    Create a Supabase client with service role key for admin operations.
    
    Args:
        url: Supabase project URL
        service_key: Supabase service role key
        
    Returns:
        Supabase admin client or None if not available
    """
    if not SUPABASE_AVAILABLE:
        return None
    
    if not url or not service_key:
        return None
    
    return create_client(url, service_key)


class BaseDatabase:
    """
    Base database class for puzzle storage and authentication.
    Each language version extends this with its own Supabase credentials.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, supabase_service_key: str = "", admin_secret: str = ""):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_service_key = supabase_service_key
        self.admin_secret = admin_secret
        self._client: Any = None
        self._admin_client: Any = None
    
    @property
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.supabase_url and self.supabase_key)
    
    @property
    def client(self) -> Any:
        """Get or create Supabase client."""
        if self._client is None and self.is_configured:
            self._client = get_supabase_client(self.supabase_url, self.supabase_key)
        return self._client
    
    @property
    def admin_client(self) -> Any:
        """Get or create Supabase admin client."""
        if self._admin_client is None and self.supabase_url and self.supabase_service_key:
            self._admin_client = get_supabase_admin_client(self.supabase_url, self.supabase_service_key)
        return self._admin_client
    
    # =========================================================================
    # AUTHENTICATION FUNCTIONS
    # =========================================================================
    
    async def sign_in_with_email(self, email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Sign in a user with email and password using Supabase Auth.
        Returns (user_data, error_message).
        """
        client = self.client
        if not client:
            # Fallback to simple password check if Supabase is not configured
            if password == self.admin_secret and self.admin_secret != "change-me-in-production":
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
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out a user."""
        client = self.client
        if not client:
            return True
        
        try:
            client.auth.sign_out()
            return True
        except Exception:
            return True  # Consider signed out even if error
    
    async def verify_session(self, access_token: str) -> Optional[Dict]:
        """Verify an access token and return user data if valid."""
        client = self.client
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
    
    async def refresh_session(self, refresh_token: str) -> Optional[Dict]:
        """Refresh an expired session using a refresh token."""
        client = self.client
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
    
    # =========================================================================
    # PUZZLE FUNCTIONS
    # =========================================================================
    
    async def get_all_puzzles(self) -> List[Dict]:
        """Fetch all puzzles from Supabase."""
        client = self.client
        if not client:
            return []
        
        try:
            response = client.table("puzzles").select("*").order("created_at", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching puzzles: {e}")
            return []
    
    async def get_active_puzzles(self) -> List[Dict]:
        """Fetch only active puzzles from Supabase."""
        client = self.client
        if not client:
            return []
        
        try:
            response = client.table("puzzles").select("*").eq("active", True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching active puzzles: {e}")
            return []
    
    async def get_puzzle_by_date(self, date_str: str) -> Optional[Dict]:
        """Get a specific puzzle assigned to a date."""
        client = self.client
        if not client:
            return None
        
        try:
            response = client.table("puzzles").select("*").eq("scheduled_date", date_str).single().execute()
            return response.data
        except Exception:
            return None
    
    async def add_puzzle(self, puzzle: Dict) -> Optional[Dict]:
        """Add a new puzzle to Supabase."""
        client = self.admin_client
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
    
    async def add_puzzles_bulk(self, puzzles: List[Dict]) -> List[Dict]:
        """Add multiple puzzles to Supabase."""
        client = self.admin_client
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
            if "duplicate" in error_msg.lower():
                raise ValueError(f"Duplicate puzzle detected: {error_msg}")
            raise ValueError(f"Database error: {error_msg}")
    
    async def update_puzzle(self, puzzle_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing puzzle."""
        client = self.admin_client
        if not client:
            return None
        
        try:
            response = client.table("puzzles").update(updates).eq("id", puzzle_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating puzzle: {e}")
            return None
    
    async def delete_puzzle(self, puzzle_id: str) -> bool:
        """Delete a puzzle."""
        client = self.admin_client
        if not client:
            return False
        
        try:
            client.table("puzzles").delete().eq("id", puzzle_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting puzzle: {e}")
            return False
    
    async def schedule_puzzle(self, puzzle_id: str, date_str: str) -> Optional[Dict]:
        """Schedule a puzzle for a specific date."""
        client = self.admin_client
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
    
    @staticmethod
    def get_daily_puzzle_index(puzzles_count: int, date_str: str) -> int:
        """
        Get the puzzle index for a given date.
        Uses a hash to ensure consistent puzzle selection.
        """
        if puzzles_count == 0:
            return 0
        hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
        return hash_value % puzzles_count
