"""
Arabic Language Configuration for kalimle.
Contains Arabic-specific word validation, normalization, and keyboard layout.
"""
from typing import List, Dict
import sys
import os

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.game.logic import BaseWordValidator


# Arabic diacritics (tashkeel) - these don't count as letters
ARABIC_DIACRITICS = '\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670'


# Arabic keyboard layout
KEYBOARD_LAYOUT = [
    ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج'],
    ['ش', 'س', 'ي', 'ب', 'ل', 'ا', 'ت', 'ن', 'م', 'ك', 'ة'],
    ['ط', 'ء', 'ؤ', 'ر', 'ى', 'ئ', 'و', 'ز', 'ظ', 'د', 'ذ'],
]


# Fallback puzzles when database is not configured
FALLBACK_PUZZLES: List[dict] = [
    {
        "sentence": "I am reading a ___.",
        "target": "كتاب",
        "pronunciation": "kitāb",
        "meaning": "book",
        "example": "أقرأ كتاباً ممتعاً"
    },
    {
        "sentence": "The ___ is shining brightly today.",
        "target": "شمس",
        "pronunciation": "shams",
        "meaning": "sun",
        "example": "الشمس مشرقة اليوم"
    },
    {
        "sentence": "I drink ___ every morning.",
        "target": "قهوة",
        "pronunciation": "qahwa",
        "meaning": "coffee",
        "example": "أشرب القهوة كل صباح"
    },
    {
        "sentence": "The ___ is very blue today.",
        "target": "سماء",
        "pronunciation": "samāʾ",
        "meaning": "sky",
        "example": "السماء زرقاء جميلة"
    },
    {
        "sentence": "I love to eat ___.",
        "target": "تفاح",
        "pronunciation": "tuffāḥ",
        "meaning": "apple",
        "example": "أحب أكل التفاح"
    },
    {
        "sentence": "My ___ is very kind.",
        "target": "صديق",
        "pronunciation": "ṣadīq",
        "meaning": "friend",
        "example": "صديقي طيب جداً"
    },
    {
        "sentence": "I live in a big ___.",
        "target": "مدينة",
        "pronunciation": "madīna",
        "meaning": "city",
        "example": "أسكن في مدينة كبيرة"
    },
]


class ArabicWordValidator(BaseWordValidator):
    """
    Arabic word validator with language-specific normalization rules.
    """
    
    LANGUAGE_CODE = "ar"
    LANGUAGE_NAME = "Arabic"
    APP_NAME = "kalimle"
    
    # Define letter equivalence groups
    ALIF_VARIATIONS = {'ا', 'أ', 'إ', 'آ', 'ٱ'}
    HAMZA_VARIATIONS = {'ء', 'ؤ', 'ئ'}
    HA_TA_VARIATIONS = {'ه', 'ة'}
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize Arabic text by removing diacritics and normalizing characters.
        
        Rules:
        - Removes all Arabic diacritics (tashkeel)
        - Normalizes alif variations (أ إ آ ٱ) to plain alif (ا)
        - Keeps hamza forms (ء ؤ ئ) and teh marbuta (ة) as distinct characters
        """
        # Remove diacritics
        text = self.remove_diacritics(text)
        
        # Normalize only alif variations to plain alif
        text = text.replace('أ', 'ا')
        text = text.replace('إ', 'ا')
        text = text.replace('آ', 'ا')
        text = text.replace('ٱ', 'ا')
        
        # Keep these as distinct characters:
        # ء (standalone hamza)
        # ؤ (hamza on waw)
        # ئ (hamza on yeh)
        # ة (teh marbuta)
        
        return text.strip()
    
    def letters_match(self, guess_letter: str, target_letter: str) -> bool:
        """
        Check if two letters match, considering Arabic equivalences.
        Returns True if they're the same or in the same equivalence group.
        """
        # Exact match
        if guess_letter == target_letter:
            return True
        
        # Check alif variations
        if guess_letter in self.ALIF_VARIATIONS and target_letter in self.ALIF_VARIATIONS:
            return True
        
        # Check hamza variations
        if guess_letter in self.HAMZA_VARIATIONS and target_letter in self.HAMZA_VARIATIONS:
            return True
        
        # Check ha/ta marbuta
        if guess_letter in self.HA_TA_VARIATIONS and target_letter in self.HA_TA_VARIATIONS:
            return True
        
        return False
    
    def validate_guess(self, guess: str, target: str) -> List[Dict]:
        """
        Validate a guess against the target word with Arabic-specific rules.
        
        - Treats alif variations (ا أ إ آ) as equivalent
        - Treats hamza variations (ء ؤ ئ) as equivalent
        - Treats ه and ة as equivalent
        - When correct, displays the actual letter from the target
        - Marks keyboard with the canonical form of equivalent letters
        """
        from typing import Dict, List
        
        # Remove diacritics from both
        guess_clean = self.remove_diacritics(guess)
        target_clean = self.remove_diacritics(target)
        
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
        guess_clean = self.remove_diacritics(guess)
        target_clean = self.remove_diacritics(target)
        
        if len(guess_clean) != len(target_clean):
            return False
        
        # Check each letter using equivalence rules
        for i in range(len(guess_clean)):
            if not self.letters_match(guess_clean[i], target_clean[i]):
                return False
        
        return True
    
    def count_letters(self, text: str) -> int:
        """
        Count the number of actual Arabic letters (excluding diacritics).
        """
        clean_text = self.remove_diacritics(text)
        return len(clean_text.strip())
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        """Remove Arabic diacritics from text."""
        for d in ARABIC_DIACRITICS:
            text = text.replace(d, '')
        return text


# Create a singleton instance for easy import
validator = ArabicWordValidator()


# Language-specific configuration
LANGUAGE_CONFIG = {
    "code": "ar",
    "name": "Arabic",
    "app_name": "kalimle",
    "text_direction": "rtl",
    "meta_description": "Daily Arabic word puzzle game - Guess the Arabic word that fills the blank",
    "keyboard_layout": KEYBOARD_LAYOUT,
    "fallback_puzzles": FALLBACK_PUZZLES,
    "help_text": {
        "title": "How to Play",
        "description": "Guess the Arabic word that fills the blank in 6 tries.",
        "rules": [
            "Each guess must be a valid Arabic word",
            "The word must match the length shown",
            "After each guess, the color of the tiles will show how close you are"
        ],
        "letter_rules": {
            "title": "Arabic Letter Rules",
            "alif_note": "✨ Alif equivalence: أ إ آ ٱ all match ا (and vice versa)",
            "distinct_note": "✨ Hamza equivalence: ء ؤ ئ all match each other | ✨ ه and ة match each other",
            "usage_note": "When correct, the tile shows the exact letter from the answer. All equivalent forms are marked on the keyboard!"
        }
    }
}
