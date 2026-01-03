"""
Shared game logic module.
"""

from .logic import (
    BaseWordValidator,
    get_today_gmt,
    get_game_state_key,
    MAX_GUESSES
)

__all__ = [
    "BaseWordValidator",
    "get_today_gmt",
    "get_game_state_key",
    "MAX_GUESSES"
]
