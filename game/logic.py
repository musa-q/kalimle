"""
kalimle - Daily Word Puzzle Game
A FastAPI application where players guess Arabic words to fill in English sentence blanks.
"""
from datetime import date, datetime, timezone
from typing import List, Tuple, Dict, Optional
import hashlib
import asyncio

# Daily puzzles - Each entry contains:
# (English sentence with blank, Arabic target word, pronunciation, example sentence in Arabic)
# These are fallback puzzles used when Supabase is not configured
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

# Cache for database puzzles
_cached_puzzles: List[Dict] = []
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_today_gmt() -> date:
    """Get today's date in GMT/UTC timezone."""
    return datetime.now(timezone.utc).date()


def get_daily_puzzle_index() -> int:
    """
    Get the puzzle index for today based on the current GMT date.
    Uses a hash to ensure the same puzzle for all players worldwide.
    """
    today = get_today_gmt()
    # Create a consistent hash from the date
    date_str = today.isoformat()
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    return hash_value % len(DAILY_PUZZLES)


async def _fetch_puzzles_from_db() -> List[Dict]:
    """Fetch puzzles from database with caching."""
    global _cached_puzzles, _cache_timestamp
    
    now = datetime.now(timezone.utc)
    
    # Check if cache is still valid
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
        if _cached_puzzles:
            return _cached_puzzles
    
    # Try to import database module
    try:
        import database
        puzzles = await database.get_active_puzzles()
        if puzzles:
            _cached_puzzles = puzzles
            _cache_timestamp = now
            return puzzles
    except Exception as e:
        print(f"Error fetching puzzles from database: {e}")
    
    return []


def _fetch_puzzles_sync() -> List[Dict]:
    """Synchronous wrapper to fetch puzzles from database."""
    global _cached_puzzles, _cache_timestamp
    
    now = datetime.now(timezone.utc)
    
    # Check if cache is still valid
    if _cache_timestamp and (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
        if _cached_puzzles:
            return _cached_puzzles
    
    # Try to fetch from database
    try:
        import database
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context - just use cache or fallback
            # The async route handlers will populate the cache
            return _cached_puzzles if _cached_puzzles else []
        except RuntimeError:
            # No running loop - we can create one
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                puzzles = loop.run_until_complete(database.get_active_puzzles())
                if puzzles:
                    _cached_puzzles = puzzles
                    _cache_timestamp = now
                    return puzzles
            finally:
                loop.close()
    except Exception as e:
        print(f"Error fetching puzzles from database: {e}")
    
    return []


def _get_puzzle_for_date(puzzles: List[Dict], date_obj: date) -> Dict:
    """Select puzzle for a specific date from a list of puzzles."""
    date_str = date_obj.isoformat()
    
    # First, check if there's a puzzle scheduled for this specific date
    for puzzle in puzzles:
        if puzzle.get("scheduled_date") == date_str:
            return puzzle
    
    # Otherwise, use hash-based selection from active puzzles
    if puzzles:
        hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
        index = hash_value % len(puzzles)
        return puzzles[index]
    
    # Fallback to local puzzles
    return DAILY_PUZZLES[get_daily_puzzle_index()]


def get_todays_puzzle() -> Dict:
    """
    Get today's puzzle dictionary.
    Uses GMT timezone to ensure consistent puzzle for all users.
    Tries to fetch from database first, falls back to local puzzles.
    """
    today = get_today_gmt()
    
    # Try to get puzzles from database
    try:
        puzzles = _fetch_puzzles_sync()
        if puzzles:
            return _get_puzzle_for_date(puzzles, today)
    except Exception as e:
        print(f"Error in get_todays_puzzle: {e}")
    
    # Fallback to local puzzles
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
    Only normalizes alif variations (أ إ آ) to plain alif (ا).
    Keeps hamza forms (ء ؤ ئ) and teh marbuta (ة) as distinct characters.
    """
    # Remove diacritics
    text = remove_diacritics(text)

    # Normalize only alif variations to plain alif
    # This includes: أ إ آ ٱ
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
    """Generate a unique key for today's game state based on GMT date."""
    return get_today_gmt().isoformat()
