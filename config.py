"""
Configuration management for kalimle app.
Uses environment variables for Railway deployment.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # anon/public key
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")  # service role key for admin ops
    
    # Admin Configuration
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "change-me-in-production")
    
    # App Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
