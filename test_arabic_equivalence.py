"""
Test Arabic letter equivalence feature.
Tests that alif, hamza, and ha/ta variations are treated as equivalent.
"""
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arabic.language_config import ArabicWordValidator


def test_alif_equivalence():
    """Test that all alif variations match each other."""
    validator = ArabicWordValidator()
    
    # Test alif variations matching plain alif
    assert validator.letters_match('أ', 'ا'), "أ should match ا"
    assert validator.letters_match('إ', 'ا'), "إ should match ا"
    assert validator.letters_match('آ', 'ا'), "آ should match ا"
    assert validator.letters_match('ٱ', 'ا'), "ٱ should match ا"
    
    # Test reverse
    assert validator.letters_match('ا', 'أ'), "ا should match أ"
    assert validator.letters_match('ا', 'إ'), "ا should match إ"
    
    # Test variations matching each other
    assert validator.letters_match('أ', 'إ'), "أ should match إ"
    assert validator.letters_match('آ', 'أ'), "آ should match أ"
    
    print("✓ Alif equivalence tests passed")


def test_hamza_equivalence():
    """Test that all hamza variations match each other."""
    validator = ArabicWordValidator()
    
    # Test hamza variations
    assert validator.letters_match('ء', 'ؤ'), "ء should match ؤ"
    assert validator.letters_match('ء', 'ئ'), "ء should match ئ"
    assert validator.letters_match('ؤ', 'ئ'), "ؤ should match ئ"
    
    # Test reverse
    assert validator.letters_match('ؤ', 'ء'), "ؤ should match ء"
    assert validator.letters_match('ئ', 'ء'), "ئ should match ء"
    
    print("✓ Hamza equivalence tests passed")


def test_ha_ta_equivalence():
    """Test that ه and ة match each other."""
    validator = ArabicWordValidator()
    
    assert validator.letters_match('ه', 'ة'), "ه should match ة"
    assert validator.letters_match('ة', 'ه'), "ة should match ه"
    
    print("✓ Ha/Ta marbuta equivalence tests passed")


def test_non_equivalent_letters():
    """Test that non-equivalent letters don't match."""
    validator = ArabicWordValidator()
    
    # Alif should not match hamza
    assert not validator.letters_match('ا', 'ء'), "ا should not match ء"
    
    # Alif should not match ha
    assert not validator.letters_match('ا', 'ه'), "ا should not match ه"
    
    # Regular letters should not match
    assert not validator.letters_match('ب', 'ت'), "ب should not match ت"
    assert not validator.letters_match('س', 'ش'), "س should not match ش"
    
    print("✓ Non-equivalent letters tests passed")


def test_validate_guess_with_equivalence():
    """Test that validate_guess correctly handles equivalent letters."""
    validator = ArabicWordValidator()
    
    # Test guessing with different alif form
    target = "كتاب"  # kitab with plain alif
    guess = "كتأب"   # kitab with alif hamza above
    
    result = validator.validate_guess(guess, target)
    
    # The result should show all correct (green)
    assert len(result) == 4, "Result should have 4 letters"
    
    # Check first letter (ك)
    assert result[0]['letter'] == 'ك', "First letter should be ك"
    assert result[0]['status'] == 'correct', "First letter should be correct"
    
    # Check third letter (alif) - should show target's ا not guessed أ
    assert result[2]['letter'] == 'ا', "Third letter should be ا (from target)"
    assert result[2]['status'] == 'correct', "Third letter should be correct"
    
    print("✓ Validate guess with equivalence tests passed")


def test_hamza_in_guess():
    """Test guessing with different hamza forms."""
    validator = ArabicWordValidator()
    
    # Target has ء, guess has ؤ
    target = "شيء"  # thing
    guess = "شيؤ"   # thing with hamza on waw
    
    result = validator.validate_guess(guess, target)
    
    # Last letter should match and show target's ء
    assert result[2]['letter'] == 'ء', "Should show target's ء"
    assert result[2]['status'] == 'correct', "Should be correct"
    
    print("✓ Hamza in guess tests passed")


def test_ha_ta_in_guess():
    """Test guessing with ه when answer has ة."""
    validator = ArabicWordValidator()
    
    # Target has ة, guess has ه
    target = "مدرسة"  # school
    guess = "مدرسه"   # school with regular ha
    
    result = validator.validate_guess(guess, target)
    
    # Last letter should match and show target's ة
    assert result[4]['letter'] == 'ة', "Should show target's ة"
    assert result[4]['status'] == 'correct', "Should be correct"
    
    print("✓ Ha/Ta marbuta in guess tests passed")


if __name__ == "__main__":
    try:
        test_alif_equivalence()
        test_hamza_equivalence()
        test_ha_ta_equivalence()
        test_non_equivalent_letters()
        test_validate_guess_with_equivalence()
        test_hamza_in_guess()
        test_ha_ta_in_guess()
        
        print("\n✅ All tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
