"""
Shared database module.
"""

from .base import (
    BaseDatabase,
    get_supabase_client,
    get_supabase_admin_client
)

__all__ = [
    "BaseDatabase",
    "get_supabase_client",
    "get_supabase_admin_client"
]
