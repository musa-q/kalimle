"""
Arabic Wordle - Daily Word Puzzle Game
A FastAPI application where players guess Arabic words to fill in English sentence blanks.
"""
from datetime import date
from typing import List, Tuple, Dict, Optional
import hashlib

# Daily puzzles - Each entry contains:
# (English sentence with blank, Arabic target word, pronunciation, example sentence in Arabic)
DAILY_PUZZLES: List[Dict] = [
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
    {
        "sentence": "The ___ is cold in winter.",
        "target": "ماء",
        "pronunciation": "māʾ",
        "meaning": "water",
        "example": "الماء بارد في الشتاء"
    },
    {
        "sentence": "I need to buy some ___.",
        "target": "خبز",
        "pronunciation": "khubz",
        "meaning": "bread",
        "example": "أحتاج لشراء الخبز"
    },
    {
        "sentence": "The ___ in the garden is beautiful.",
        "target": "وردة",
        "pronunciation": "warda",
        "meaning": "flower/rose",
        "example": "الوردة في الحديقة جميلة"
    },
    {
        "sentence": "I have a small ___.",
        "target": "بيت",
        "pronunciation": "bayt",
        "meaning": "house",
        "example": "عندي بيت صغير"
    },
    {
        "sentence": "The ___ was delicious.",
        "target": "طعام",
        "pronunciation": "ṭaʿām",
        "meaning": "food",
        "example": "الطعام كان لذيذاً"
    },
    {
        "sentence": "I saw a beautiful ___ at the zoo.",
        "target": "حيوان",
        "pronunciation": "ḥayawān",
        "meaning": "animal",
        "example": "رأيت حيواناً جميلاً في الحديقة"
    },
    {
        "sentence": "My ___ works at a hospital.",
        "target": "أخ",
        "pronunciation": "akh",
        "meaning": "brother",
        "example": "أخي يعمل في المستشفى"
    },
    {
        "sentence": "I wrote a long ___.",
        "target": "رسالة",
        "pronunciation": "risāla",
        "meaning": "letter/message",
        "example": "كتبت رسالة طويلة"
    },
    {
        "sentence": "The ___ teaches us every day.",
        "target": "معلم",
        "pronunciation": "muʿallim",
        "meaning": "teacher",
        "example": "المعلم يعلمنا كل يوم"
    },
    {
        "sentence": "I traveled by ___.",
        "target": "طائرة",
        "pronunciation": "ṭāʾira",
        "meaning": "airplane",
        "example": "سافرت بالطائرة"
    },
    {
        "sentence": "The ___ at night is peaceful.",
        "target": "قمر",
        "pronunciation": "qamar",
        "meaning": "moon",
        "example": "القمر في الليل جميل"
    },
    {
        "sentence": "I need to go to the ___.",
        "target": "مدرسة",
        "pronunciation": "madrasa",
        "meaning": "school",
        "example": "أحتاج للذهاب إلى المدرسة"
    },
    {
        "sentence": "This ___ is very interesting.",
        "target": "فيلم",
        "pronunciation": "fīlm",
        "meaning": "movie/film",
        "example": "هذا الفيلم ممتع جداً"
    },
    {
        "sentence": "I bought a new ___.",
        "target": "سيارة",
        "pronunciation": "sayyāra",
        "meaning": "car",
        "example": "اشتريت سيارة جديدة"
    },
    {
        "sentence": "The ___ is blowing strongly.",
        "target": "رياح",
        "pronunciation": "riyāḥ",
        "meaning": "wind",
        "example": "الرياح تهب بقوة"
    },
    {
        "sentence": "I speak ___.",
        "target": "عربي",
        "pronunciation": "ʿarabī",
        "meaning": "Arabic",
        "example": "أتكلم اللغة العربية"
    },
    {
        "sentence": "The ___ is falling from the sky.",
        "target": "مطر",
        "pronunciation": "maṭar",
        "meaning": "rain",
        "example": "المطر ينزل من السماء"
    },
    {
        "sentence": "I love my ___.",
        "target": "عائلة",
        "pronunciation": "ʿāʾila",
        "meaning": "family",
        "example": "أحب عائلتي كثيراً"
    },
    {
        "sentence": "The ___ is very tall.",
        "target": "شجرة",
        "pronunciation": "shajara",
        "meaning": "tree",
        "example": "الشجرة طويلة جداً"
    },
    {
        "sentence": "I work at an ___.",
        "target": "مكتب",
        "pronunciation": "maktab",
        "meaning": "office",
        "example": "أعمل في مكتب"
    },
    {
        "sentence": "The ___ is singing.",
        "target": "طائر",
        "pronunciation": "ṭāʾir",
        "meaning": "bird",
        "example": "الطائر يغني"
    },
    {
        "sentence": "I take ___ for my health.",
        "target": "دواء",
        "pronunciation": "dawāʾ",
        "meaning": "medicine",
        "example": "آخذ الدواء لصحتي"
    },
    {
        "sentence": "The ___ is very big.",
        "target": "بحر",
        "pronunciation": "baḥr",
        "meaning": "sea",
        "example": "البحر كبير جداً"
    },
]

MAX_GUESSES = 6


def get_daily_puzzle_index() -> int:
    """
    Get the puzzle index for today based on the current date.
    Uses a hash to ensure the same puzzle for all players worldwide.
    """
    today = date.today()
    # Create a consistent hash from the date
    date_str = today.isoformat()
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    return hash_value % len(DAILY_PUZZLES)


def get_todays_puzzle() -> Dict:
    """Get today's puzzle dictionary."""
    index = get_daily_puzzle_index()
    return DAILY_PUZZLES[index]


# Arabic diacritics (tashkeel) - these don't count as letters
ARABIC_DIACRITICS = '\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670'


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics from text."""
    for d in ARABIC_DIACRITICS:
        text = text.replace(d, '')
    return text


def count_arabic_letters(text: str) -> int:
    """
    Count the number of actual Arabic letters (excluding diacritics).
    """
    # Remove diacritics first
    clean_text = remove_diacritics(text)
    # Count remaining characters (excluding whitespace)
    return len(clean_text.strip())


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text by removing diacritics and normalizing characters.
    """
    # Remove diacritics
    text = remove_diacritics(text)
    
    # Normalize alef variations
    text = text.replace('أ', 'ا')
    text = text.replace('إ', 'ا')
    text = text.replace('آ', 'ا')
    text = text.replace('ٱ', 'ا')
    
    # Normalize teh marbuta and heh
    text = text.replace('ة', 'ه')
    
    # Normalize yeh variations
    text = text.replace('ى', 'ي')
    
    return text.strip()


def validate_guess(guess: str, target: str) -> List[Dict]:
    """
    Validate a guess against the target word.
    Returns a list of letter feedback dictionaries.
    
    Each dict contains:
    - letter: the Arabic letter
    - status: 'correct' (green), 'present' (yellow), or 'absent' (gray)
    """
    # Normalize both strings
    guess_normalized = normalize_arabic(guess)
    target_normalized = normalize_arabic(target)
    
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
    for i, letter in enumerate(guess_letters):
        normalized_letter = normalize_arabic(letter)
        if i < len(target_letters) and normalized_letter == target_letters[i]:
            temp_result[i] = {'letter': letter, 'status': 'correct'}
            target_letter_counts[normalized_letter] -= 1
    
    # Second pass: mark present but wrong position (yellow) or absent (gray)
    for i, letter in enumerate(guess_letters):
        if temp_result[i] is not None:
            continue
        
        normalized_letter = normalize_arabic(letter)
        if normalized_letter in target_letter_counts and target_letter_counts[normalized_letter] > 0:
            temp_result[i] = {'letter': letter, 'status': 'present'}
            target_letter_counts[normalized_letter] -= 1
        else:
            temp_result[i] = {'letter': letter, 'status': 'absent'}
    
    return temp_result


def check_win(guess: str, target: str) -> bool:
    """Check if the guess matches the target word."""
    return normalize_arabic(guess) == normalize_arabic(target)


def validate_guess_length(guess: str, target: str) -> Tuple[bool, str]:
    """
    Check if the guess has the correct number of letters.
    Returns (is_valid, error_message).
    """
    guess_len = count_arabic_letters(guess)
    target_len = count_arabic_letters(target)
    
    if guess_len == 0:
        return False, "Please enter a guess"
    elif guess_len < target_len:
        return False, f"Too short! The word has {target_len} letters"
    elif guess_len > target_len:
        return False, f"Too long! The word has {target_len} letters"
    
    return True, ""


def get_game_state_key() -> str:
    """Generate a unique key for today's game state."""
    return date.today().isoformat()
