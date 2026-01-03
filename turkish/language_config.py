"""
Turkish Language Configuration for kelimle.
Contains Turkish-specific word validation, normalization, and keyboard layout.
"""
from typing import List
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
            "alif_note": "Special characters: ç, ğ, ı, ö, ş, ü are separate letters",
            "distinct_note": "İ and I are distinct letters (dotted and undotted)",
            "usage_note": "Use the correct Turkish characters as shown in the answer"
        }
    }
}
