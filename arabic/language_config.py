"""
Arabic Language Configuration for kalimle.
Contains Arabic-specific word validation, normalization, and keyboard layout.
"""
from typing import List
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
            "alif_note": "Alif variations: أ إ آ are treated as ا",
            "distinct_note": "Distinct characters: ء ؤ ئ and ة are kept separate",
            "usage_note": "Use the exact hamza form and teh marbuta as shown in the answer"
        }
    }
}
