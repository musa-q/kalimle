"""
Shared Game Logic for Multi-Language Wordle
Abstract base class and common game functions that work across all languages.
"""
from datetime import date, datetime, timezone
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
import hashlib

MAX_GUESSES = 6


def get_today_gmt() -> date:
    """Get today's date in GMT/UTC timezone."""
    return datetime.now(timezone.utc).date()


def get_game_state_key() -> str:
    """Generate a unique key for today's game state based on GMT date."""
    return get_today_gmt().isoformat()


def get_puzzle_index_for_date(puzzles_count: int, date_obj: date) -> int:
    """
    Get the puzzle index for a given date using hash-based selection.
    Ensures the same puzzle for all players worldwide.
    """
    if puzzles_count == 0:
        return 0
    date_str = date_obj.isoformat()
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    return hash_value % puzzles_count


class BaseWordValidator(ABC):
    """
    Abstract base class for language-specific word validation.
    Each language implements its own normalization rules.
    """
    
    # Override these in subclasses
    LANGUAGE_CODE: str = "en"
    LANGUAGE_NAME: str = "English"
    APP_NAME: str = "Wordle"
    
    @abstractmethod
    def normalize_text(self, text: str) -> str:
        """
        Normalize text according to language-specific rules.
        This handles character equivalences, diacritics removal, etc.
        
        Args:
            text: The raw text to normalize
            
        Returns:
            Normalized text for comparison
        """
        pass
    
    @abstractmethod
    def count_letters(self, text: str) -> int:
        """
        Count the number of actual letters in text.
        Excludes diacritics, spaces, and other non-letter characters.
        
        Args:
            text: The text to count letters in
            
        Returns:
            Number of letters
        """
        pass
    
    def validate_guess(self, guess: str, target: str) -> List[Dict]:
        """
        Validate a guess against the target word.
        Returns a list of letter feedback dictionaries.
        
        Each dict contains:
        - letter: the letter (as displayed)
        - status: 'correct' (green), 'present' (yellow), or 'absent' (gray)
        
        This is the core Wordle algorithm, shared across all languages.
        """
        # Normalize both strings for comparison
        guess_normalized = self.normalize_text(guess)
        target_normalized = self.normalize_text(target)
        
        # Use original guess letters for display but normalized for comparison
        guess_letters = list(guess)
        target_letters = list(target_normalized)
        
        result = []
        target_letter_counts = {}
        
        # Count letters in target
        for letter in target_letters:
            target_letter_counts[letter] = target_letter_counts.get(letter, 0) + 1
        
        # First pass: mark correct positions (green)
        temp_result = [None] * len(guess_letters)
        target_display_letters = list(target)  # Original target letters for display
        for i, letter in enumerate(guess_letters):
            normalized_letter = self.normalize_text(letter)
            if i < len(target_letters) and normalized_letter == target_letters[i]:
                temp_result[i] = {
                    'letter': letter,
                    'status': 'correct',
                    'keyboard_letter': target_display_letters[i] if i < len(target_display_letters) else letter,
                    'guessed_letter': letter
                }
                target_letter_counts[normalized_letter] -= 1
        
        # Second pass: mark present but wrong position (yellow) or absent (gray)
        for i, letter in enumerate(guess_letters):
            if temp_result[i] is not None:
                continue
            
            normalized_letter = self.normalize_text(letter)
            if normalized_letter in target_letter_counts and target_letter_counts[normalized_letter] > 0:
                temp_result[i] = {
                    'letter': letter,
                    'status': 'present',
                    'keyboard_letter': target_display_letters[i] if i < len(target_display_letters) else letter,
                    'guessed_letter': letter
                }
                target_letter_counts[normalized_letter] -= 1
            else:
                temp_result[i] = {
                    'letter': letter,
                    'status': 'absent',
                    'keyboard_letter': target_display_letters[i] if i < len(target_display_letters) else letter,
                    'guessed_letter': letter
                }
        
        return temp_result
    
    def check_win(self, guess: str, target: str) -> bool:
        """Check if the guess matches the target word."""
        return self.normalize_text(guess) == self.normalize_text(target)
    
    def validate_guess_length(self, guess: str, target: str) -> Tuple[bool, str]:
        """
        Check if the guess has the correct number of letters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        guess_len = self.count_letters(guess)
        target_len = self.count_letters(target)
        
        if guess_len == 0:
            return False, "Please enter a guess"
        elif guess_len < target_len:
            return False, f"Too short! The word has {target_len} letters"
        elif guess_len > target_len:
            return False, f"Too long! The word has {target_len} letters"
        
        return True, ""
