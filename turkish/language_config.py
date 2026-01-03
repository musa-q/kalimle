"""
Turkish Language Configuration for kelimle.
Contains Turkish-specific word validation, normalization, and keyboard layout.
"""
from typing import List, Dict
import sys
import os

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.game.logic import BaseWordValidator


# Turkish keyboard layout (QWERTY-based with Turkish characters)
KEYBOARD_LAYOUT = [
    ['e', 'r', 't', 'y', 'u', 'ı', 'o', 'p', 'ğ', 'ü'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'ş', 'i'],
    ['z', 'c', 'v', 'b', 'n', 'm', 'ö', 'ç'],
]


# Fallback puzzles when database is not configured
FALLBACK_PUZZLES: List[dict] = [
    {
        "sentence": "I am reading a ___.",
        "target": "kitap",
        "pronunciation": "ki-tap",
        "meaning": "book",
        "example": "Güzel bir kitap okuyorum."
    },
    {
        "sentence": "The ___ is shining brightly today.",
        "target": "güneş",
        "pronunciation": "gü-neş",
        "meaning": "sun",
        "example": "Güneş bugün çok parlak."
    },
    {
        "sentence": "I drink ___ every morning.",
        "target": "kahve",
        "pronunciation": "kah-ve",
        "meaning": "coffee",
        "example": "Her sabah kahve içerim."
    },
    {
        "sentence": "The ___ is very blue today.",
        "target": "gökyüzü",
        "pronunciation": "gök-yü-zü",
        "meaning": "sky",
        "example": "Gökyüzü bugün çok mavi."
    },
    {
        "sentence": "I love to eat ___.",
        "target": "elma",
        "pronunciation": "el-ma",
        "meaning": "apple",
        "example": "Elma yemeyi çok seviyorum."
    },
    {
        "sentence": "My ___ is very kind.",
        "target": "arkadaş",
        "pronunciation": "ar-ka-daş",
        "meaning": "friend",
        "example": "Arkadaşım çok iyi biri."
    },
    {
        "sentence": "I live in a big ___.",
        "target": "şehir",
        "pronunciation": "şe-hir",
        "meaning": "city",
        "example": "Büyük bir şehirde yaşıyorum."
    },
]


class TurkishWordValidator(BaseWordValidator):
    """
    Turkish word validator with language-specific normalization rules.
    
    Turkish has special letters: ç, ğ, ı, ö, ş, ü
    Also important: İ (capital I with dot) vs I (capital dotless I)
    """
    
    LANGUAGE_CODE = "tr"
    LANGUAGE_NAME = "Turkish"
    APP_NAME = "kelimle"
    
    # Define letter equivalence groups
    C_VARIATIONS = {'c', 'ç'}
    G_VARIATIONS = {'g', 'ğ'}
    I_VARIATIONS = {'i', 'ı'}
    O_VARIATIONS = {'o', 'ö'}
    S_VARIATIONS = {'s', 'ş'}
    U_VARIATIONS = {'u', 'ü'}
    
    # Turkish-specific character mappings for case-insensitive comparison
    # Turkish has special I/İ and ı/i rules
    LOWER_MAP = {
        'İ': 'i',  # Capital I with dot -> lowercase i with dot
        'I': 'ı',  # Capital dotless I -> lowercase dotless i
    }
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize Turkish text for comparison.
        
        Rules:
        - Convert to lowercase using Turkish-aware rules
        - İ (capital I with dot) -> i
        - I (capital dotless I) -> ı
        - Handle ğ, ü, ş, ö, ç as distinct characters
        """
        # Apply Turkish-specific uppercase to lowercase mappings first
        for upper, lower in self.LOWER_MAP.items():
            text = text.replace(upper, lower)
        
        # Standard lowercase for remaining characters
        text = text.lower()
        
        return text.strip()
    
    def letters_match(self, guess_letter: str, target_letter: str) -> bool:
        """
        Check if two letters match, considering Turkish equivalences.
        Returns True if they're the same or in the same equivalence group.
        """
        # Exact match
        if guess_letter == target_letter:
            return True
        
        # Check c/ç variations
        if guess_letter in self.C_VARIATIONS and target_letter in self.C_VARIATIONS:
            return True
        
        # Check g/ğ variations
        if guess_letter in self.G_VARIATIONS and target_letter in self.G_VARIATIONS:
            return True
        
        # Check i/ı variations
        if guess_letter in self.I_VARIATIONS and target_letter in self.I_VARIATIONS:
            return True
        
        # Check o/ö variations
        if guess_letter in self.O_VARIATIONS and target_letter in self.O_VARIATIONS:
            return True
        
        # Check s/ş variations
        if guess_letter in self.S_VARIATIONS and target_letter in self.S_VARIATIONS:
            return True
        
        # Check u/ü variations
        if guess_letter in self.U_VARIATIONS and target_letter in self.U_VARIATIONS:
            return True
        
        return False
    
    def validate_guess(self, guess: str, target: str) -> List[Dict]:
        """
        Validate a guess against the target word with Turkish-specific rules.
        
        - Treats c/ç as equivalent
        - Treats g/ğ as equivalent
        - Treats o/ö as equivalent
        - Treats s/ş as equivalent
        - Treats u/ü as equivalent
        - When correct, displays the actual letter from the target
        - Marks keyboard with the canonical form of equivalent letters
        """
        from typing import Dict, List
        
        # Normalize both
        guess_clean = self.normalize_text(guess)
        target_clean = self.normalize_text(target)
        
        guess_letters = list(guess_clean)
        target_letters = list(target_clean)
        
        result = []
        target_letter_counts = {}
        
        # Count letters in target (using actual target letters)
        for letter in target_letters:
            target_letter_counts[letter] = target_letter_counts.get(letter, 0) + 1
        
        # First pass: mark correct positions (green)
        temp_result = [None] * len(guess_letters)
        for i, guess_letter in enumerate(guess_letters):
            if i < len(target_letters):
                target_letter = target_letters[i]
                if self.letters_match(guess_letter, target_letter):
                    # Use the actual target letter for display
                    temp_result[i] = {
                        'letter': target_letter,
                        'status': 'correct',
                        'keyboard_letter': target_letter,  # Mark keyboard with target letter
                        'guessed_letter': guess_letter  # Track what was actually typed
                    }
                    target_letter_counts[target_letter] -= 1
        
        # Second pass: mark present but wrong position (yellow) or absent (gray)
        for i, guess_letter in enumerate(guess_letters):
            if temp_result[i] is not None:
                continue
            
            # Check if this guessed letter matches any remaining target letter
            found = False
            for target_letter, count in target_letter_counts.items():
                if count > 0 and self.letters_match(guess_letter, target_letter):
                    # Use the actual target letter for display
                    temp_result[i] = {
                        'letter': target_letter,
                        'status': 'present',
                        'keyboard_letter': target_letter,  # Mark keyboard with target letter
                        'guessed_letter': guess_letter  # Track what was actually typed
                    }
                    target_letter_counts[target_letter] -= 1
                    found = True
                    break
            
            if not found:
                temp_result[i] = {
                    'letter': guess_letter,
                    'status': 'absent',
                    'keyboard_letter': guess_letter,
                    'guessed_letter': guess_letter
                }
        
        return temp_result
    
    def check_win(self, guess: str, target: str) -> bool:
        """Check if the guess matches the target word using equivalence rules."""
        guess_clean = self.normalize_text(guess)
        target_clean = self.normalize_text(target)
        
        if len(guess_clean) != len(target_clean):
            return False
        
        # Check each letter using equivalence rules
        for i in range(len(guess_clean)):
            if not self.letters_match(guess_clean[i], target_clean[i]):
                return False
        
        return True
    
    def count_letters(self, text: str) -> int:
        """
        Count the number of letters in Turkish text.
        Turkish is mostly 1:1 letter mapping, so this is straightforward.
        """
        # Remove whitespace and count
        return len(text.strip())


# Create a singleton instance for easy import
validator = TurkishWordValidator()


# Language-specific configuration
LANGUAGE_CONFIG = {
    "code": "tr",
    "name": "Turkish",
    "app_name": "sözle",
    "text_direction": "ltr",
    "meta_description": "Daily Turkish word puzzle game - Guess the Turkish word that fills the blank",
    "keyboard_layout": KEYBOARD_LAYOUT,
    "fallback_puzzles": FALLBACK_PUZZLES,
    "help_text": {
        "title": "How to Play",
        "description": "Guess the Turkish word that fills the blank in 6 tries.",
        "rules": [
            "Each guess must be a valid Turkish word",
            "The word must match the length shown",
            "After each guess, the color of the tiles will show how close you are"
        ],
        "letter_rules": {
            "title": "Turkish Letter Rules",
            "alif_note": "✨ Letter equivalences: c/ç, g/ğ, i/ı, o/ö, s/ş, u/ü all match their pairs",
            "distinct_note": "When correct, the tile shows the exact letter from the answer",
            "usage_note": "When correct, the tile shows the exact letter from the answer. All equivalent forms are marked on the keyboard!"
        }
    }
}
