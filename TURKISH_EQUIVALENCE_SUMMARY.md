# Turkish Letter Equivalence Implementation

## Overview
Implemented letter equivalence handling for Turkish language to treat similar letters as matching in the Wordle game.

## Equivalent Letter Pairs
The following Turkish letter pairs are now treated as equivalent:
- **C ↔ Ç** (c and ç)
- **G ↔ Ğ** (g and ğ)
- **O ↔ Ö** (o and ö)
- **S ↔ Ş** (s and ş)
- **U ↔ Ü** (u and ü)

## Implementation Details

### Changes to `turkish/language_config.py`

1. **Added equivalence groups** (lines 90-94):
   ```python
   C_VARIATIONS = {'c', 'ç'}
   G_VARIATIONS = {'g', 'ğ'}
   O_VARIATIONS = {'o', 'ö'}
   S_VARIATIONS = {'s', 'ş'}
   U_VARIATIONS = {'u', 'ü'}
   ```

2. **Added `letters_match()` method** to check if two letters are equivalent:
   - Returns `True` for exact matches
   - Returns `True` if both letters are in the same equivalence group
   - Returns `False` otherwise

3. **Added `validate_guess()` method** with Turkish-specific rules:
   - Treats equivalent letter pairs as matching
   - When letters match, displays the actual letter from the target word
   - Marks the keyboard with the target letter for visual feedback
   - Handles both green tiles (correct position) and yellow tiles (wrong position)

4. **Updated help text** to explain the equivalence rules:
   ```
   "✨ Letter equivalences: c/ç, g/ğ, o/ö, s/ş, u/ü all match their pairs"
   ```

## Game Behavior

### Green Tiles (Correct Position)
- If you guess "ç" and the target has "c" in that position, you get a green tile
- The tile displays "c" (the letter from the target)
- The keyboard marks "c" as correct

### Yellow Tiles (Wrong Position)
- If you guess "ö" and the target has "o" elsewhere, you get a yellow tile
- The tile displays "o" (the letter from the target)
- The keyboard marks "o" as present

### Example
Target: `cocuk`
Guess: `çocuk`

Result: All green tiles! The guess is considered correct because c/ç are equivalent.
Display: `cocuk` (shows the actual letters from the target)

## Testing

Created comprehensive test suite in `test_turkish_equivalence.py`:
- ✅ Tests individual letter matching for all 5 equivalence pairs
- ✅ Tests full word validation with equivalences
- ✅ Tests multiple equivalences in a single word
- ✅ Tests yellow tile behavior with equivalences
- ✅ All tests passing!

## Files Modified
- `turkish/language_config.py` - Added equivalence logic
- `test_turkish_equivalence.py` - Created test suite

## Consistency with Arabic Implementation
This implementation follows the same pattern as the Arabic letter equivalence system, ensuring consistency across languages in the codebase.
