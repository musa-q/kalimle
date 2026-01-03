"""
Test Turkish letter equivalence handling in the game logic.
"""
import sys
from turkish.language_config import validator


def test_letter_matching():
    """Test that similar Turkish letters match correctly."""
    print("Testing Turkish letter equivalences...")
    
    # Test c/ç equivalence
    assert validator.letters_match('c', 'ç'), "c should match ç"
    assert validator.letters_match('ç', 'c'), "ç should match c"
    assert validator.letters_match('c', 'c'), "c should match c"
    assert validator.letters_match('ç', 'ç'), "ç should match ç"
    print("✓ c/ç equivalence works")
    
    # Test g/ğ equivalence
    assert validator.letters_match('g', 'ğ'), "g should match ğ"
    assert validator.letters_match('ğ', 'g'), "ğ should match g"
    assert validator.letters_match('g', 'g'), "g should match g"
    assert validator.letters_match('ğ', 'ğ'), "ğ should match ğ"
    print("✓ g/ğ equivalence works")
    
    # Test o/ö equivalence
    assert validator.letters_match('o', 'ö'), "o should match ö"
    assert validator.letters_match('ö', 'o'), "ö should match o"
    assert validator.letters_match('o', 'o'), "o should match o"
    assert validator.letters_match('ö', 'ö'), "ö should match ö"
    print("✓ o/ö equivalence works")
    
    # Test s/ş equivalence
    assert validator.letters_match('s', 'ş'), "s should match ş"
    assert validator.letters_match('ş', 's'), "ş should match s"
    assert validator.letters_match('s', 's'), "s should match s"
    assert validator.letters_match('ş', 'ş'), "ş should match ş"
    print("✓ s/ş equivalence works")
    
    # Test u/ü equivalence
    assert validator.letters_match('u', 'ü'), "u should match ü"
    assert validator.letters_match('ü', 'u'), "ü should match u"
    assert validator.letters_match('u', 'u'), "u should match u"
    assert validator.letters_match('ü', 'ü'), "ü should match ü"
    print("✓ u/ü equivalence works")
    
    # Test non-equivalences
    assert not validator.letters_match('c', 'g'), "c should not match g"
    assert not validator.letters_match('o', 'u'), "o should not match u"
    assert not validator.letters_match('s', 'c'), "s should not match c"
    print("✓ Non-equivalent letters don't match")


def test_validate_guess():
    """Test complete guess validation with equivalences."""
    print("\nTesting Turkish word validation...")
    
    # Test 1: guessing 'çocuk' when answer is 'cocuk' (c/ç equivalence)
    target = "cocuk"
    guess = "çocuk"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    # All should be correct (green) and display target letters
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[0]['letter'] == 'c', "First letter should be 'c' from target"
    assert result[2]['letter'] == 'c', "Third letter should be 'c' from target"
    print("✓ c/ç equivalence works in full word validation")
    
    # Test 2: guessing 'şeker' when answer is 'seker' (s/ş equivalence)
    target = "seker"
    guess = "şeker"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[0]['letter'] == 's', "First letter should be 's' from target"
    print("✓ s/ş equivalence works in full word validation")
    
    # Test 3: guessing 'güzel' when answer is 'guzel' (u/ü equivalence)
    target = "guzel"
    guess = "güzel"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[1]['letter'] == 'u', "Second letter should be 'u' from target"
    print("✓ u/ü equivalence works in full word validation")
    
    # Test 4: Mixed equivalences - guessing 'göğüs' when answer is 'gogus'
    target = "gogus"
    guess = "göğüs"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[0]['letter'] == 'g', "First letter should be 'g' from target (o/ö match)"
    assert result[1]['letter'] == 'o', "Second letter should be 'o' from target"
    assert result[2]['letter'] == 'g', "Third letter should be 'g' from target (g/ğ match)"
    assert result[3]['letter'] == 'u', "Fourth letter should be 'u' from target"
    assert result[4]['letter'] == 's', "Fifth letter should be 's' from target"
    print("✓ Multiple equivalences work together in validation")


def test_yellow_tile_equivalence():
    """Test that equivalences work for yellow (present but wrong position) tiles."""
    print("\nTesting yellow tiles with equivalences...")
    
    # Test: guessing 'öcek' when answer is 'keco' (o/ö equivalence for yellow tile)
    target = "keco"   # o in position 3
    guess = "öcek"    # ö in position 0 (should be yellow - matches o in wrong position)
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    # Position 0: ö should match o somewhere in target (yellow)
    assert result[0]['status'] == 'present', "Position 0 should be yellow (ö matches o in position 3)"
    assert result[0]['letter'] == 'o', "Should display target's 'o'"
    
    # Position 1: c should be green (matches position 2)
    # Position 2: e should be green (matches position 1)
    print("✓ Yellow tile equivalence works")


def test_reverse_equivalence():
    """Test that equivalences work both ways (target has accented, guess has plain)."""
    print("\nTesting reverse equivalences (target accented, guess plain)...")
    
    # Test 1: target has ç, guess has c
    target = "çanak"  # ç at position 0
    guess = "canak"   # c at position 0
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[0]['letter'] == 'ç', "First letter should be 'ç' from target"
    print("✓ Reverse c/ç equivalence works")
    
    # Test 2: target has ş, guess has s
    target = "şeker"
    guess = "seker"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[0]['letter'] == 'ş', "First letter should be 'ş' from target"
    print("✓ Reverse s/ş equivalence works")


def test_multiple_same_letter():
    """Test words with multiple instances of equivalent letters."""
    print("\nTesting multiple instances of same equivalent letter...")
    
    # Test: target 'cococ' (3 c's), guess 'çoçoç' (3 ç's)
    target = "cococ"
    guess = "çoçoç"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    # All should display 'c' from target
    assert result[0]['letter'] == 'c', "Position 0 should show 'c'"
    assert result[2]['letter'] == 'c', "Position 2 should show 'c'"
    assert result[4]['letter'] == 'c', "Position 4 should show 'c'"
    print("✓ Multiple instances of c/ç equivalence works")


def test_partial_matches():
    """Test words where only some letters match."""
    print("\nTesting partial matches with equivalences...")
    
    # Test: target 'köşe', guess 'kose' (o/ö and s/ş equivalence)
    target = "köşe"
    guess = "kose"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert result[0]['status'] == 'correct', "Position 0 (k) should be green"
    assert result[1]['status'] == 'correct', "Position 1 (o/ö) should be green"
    assert result[1]['letter'] == 'ö', "Position 1 should display 'ö' from target"
    assert result[2]['status'] == 'correct', "Position 2 (s/ş) should be green"
    assert result[2]['letter'] == 'ş', "Position 2 should display 'ş' from target"
    assert result[3]['status'] == 'correct', "Position 3 (e) should be green"
    print("✓ Partial matches with equivalences work")


def test_wrong_equivalents():
    """Test that wrong equivalent letters still show as yellow/gray correctly."""
    print("\nTesting wrong positions with equivalents...")
    
    # Test: target 'ünal', guess 'nalu' (ü/u and other letters in wrong positions)
    target = "ünal"
    guess = "nalu"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    # Position 0 (n) should be yellow (n is at position 1)
    assert result[0]['status'] == 'present', "Position 0 (n) should be yellow"
    # Position 1 (a) should be yellow (a is at position 2)
    assert result[1]['status'] == 'present', "Position 1 (a) should be yellow"
    # Position 2 (l) should be yellow (l is at position 3)
    assert result[2]['status'] == 'present', "Position 2 (l) should be yellow"
    # Position 3 (u) should be yellow (matches ü at position 0)
    assert result[3]['status'] == 'present', "Position 3 (u) should be yellow (matches ü)"
    assert result[3]['letter'] == 'ü', "Position 3 should display 'ü' from target"
    print("✓ Wrong positions with equivalents handled correctly")


def test_letter_count_tracking():
    """Test that equivalent letters are counted correctly (don't double count)."""
    print("\nTesting letter count tracking with equivalences...")
    
    # Test: target 'göz' (1 ö at position 1), guess 'öza' 
    # Position 0: ö should be yellow (matches ö in position 1)
    # Position 1: z should be yellow (z is at position 2)
    # Position 2: a should be gray (not in target)
    target = "göz"
    guess = "özü"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    # The algorithm marks correct positions first
    # Position 1: z matches position 2 (should be yellow)
    # Then checks remaining: position 0 ö can match position 1 ö (yellow)
    # Position 2: ü doesn't match anything (gray)
    assert result[0]['status'] == 'present', "Position 0 should be yellow (ö matches ö in position 1)"
    assert result[1]['status'] == 'present', "Position 1 should be yellow (z matches z at position 2)"
    assert result[2]['status'] == 'absent', "Position 2 should be gray (ü/u not in target)"
    print("✓ Letter count tracking with equivalents works correctly")


def test_mixed_equivalences_complex():
    """Test complex scenarios with multiple different equivalences."""
    print("\nTesting complex mixed equivalences...")
    
    # Test: target 'büyük' (ü, ü), guess 'buyuk' (u, u)
    target = "büyük"
    guess = "buyuk"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct"
    assert result[1]['letter'] == 'ü', "Position 1 should display 'ü'"
    assert result[3]['letter'] == 'ü', "Position 3 should display 'ü'"
    print("✓ Complex mixed equivalences work")


def test_no_false_positives():
    """Test that non-equivalent letters don't match."""
    print("\nTesting no false positives...")
    
    # Test: Different non-equivalent letters should not match
    # target 'kale', guess 'köle' - ö should NOT match a (they're not equivalents)
    target = "kale"
    guess = "köle"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert result[0]['status'] == 'correct', "Position 0 (k) should be green"
    assert result[1]['status'] == 'absent', "Position 1 (ö) should be gray (doesn't match a)"
    assert result[2]['status'] == 'correct', "Position 2 (l) should be green"
    assert result[3]['status'] == 'correct', "Position 3 (e) should be green"
    print("✓ No false positives - non-equivalents don't match")
    
    # Test 2: ç should NOT match g (even though both have diacritics)
    target = "gara"
    guess = "çara"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert result[0]['status'] == 'absent', "Position 0 (ç) should be gray (doesn't match g)"
    print("✓ Different accented letters don't match each other")


def test_case_insensitivity_with_equivalents():
    """Test that case doesn't matter for equivalences."""
    print("\nTesting case insensitivity with equivalents...")
    
    # Test: target 'ÇOCUK', guess 'cocuk'
    target = "ÇOCUK"
    guess = "cocuk"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    # After normalization, both become lowercase and should match
    assert all(r['status'] == 'correct' for r in result), "All letters should be correct (case insensitive)"
    print("✓ Case insensitivity with equivalents works")


def test_all_equivalence_pairs():
    """Test all 5 equivalence pairs in one word."""
    print("\nTesting all equivalence pairs together...")
    
    # Test with a word containing all equivalences: 'çöğüş'
    target = "coğus"  # g, u, s
    guess = "çöğüş"   # ç, ö, ğ, ü, ş
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', status='{r['status']}'")
    
    assert all(r['status'] == 'correct' for r in result), "All equivalences should match"
    assert result[0]['letter'] == 'c', "Position 0 should display 'c'"
    assert result[1]['letter'] == 'o', "Position 1 should display 'o'"
    assert result[2]['letter'] == 'ğ', "Position 2 should display 'ğ'"
    assert result[3]['letter'] == 'u', "Position 3 should display 'u'"
    assert result[4]['letter'] == 's', "Position 4 should display 's'"
    print("✓ All 5 equivalence pairs work together")


def test_keyboard_letter_marking():
    """Test that keyboard letters are marked correctly."""
    print("\nTesting keyboard letter marking...")
    
    # Test: target 'çok', guess 'cok'
    target = "çok"
    guess = "cok"
    result = validator.validate_guess(guess, target)
    
    print(f"\nTest: Target='{target}', Guess='{guess}'")
    for i, r in enumerate(result):
        print(f"  Position {i}: letter='{r['letter']}', keyboard='{r['keyboard_letter']}', status='{r['status']}'")
    
    # Keyboard should be marked with the target letter (ç)
    assert result[0]['keyboard_letter'] == 'ç', "Keyboard should show 'ç' from target"
    assert result[0]['letter'] == 'ç', "Display should show 'ç' from target"
    print("✓ Keyboard letter marking works correctly")


if __name__ == "__main__":
    try:
        test_letter_matching()
        test_validate_guess()
        test_yellow_tile_equivalence()
        test_reverse_equivalence()
        test_multiple_same_letter()
        test_partial_matches()
        test_wrong_equivalents()
        test_letter_count_tracking()
        test_mixed_equivalences_complex()
        test_no_false_positives()
        test_case_insensitivity_with_equivalents()
        test_all_equivalence_pairs()
        test_keyboard_letter_marking()
        print("\n" + "="*50)
        print("🎉 All Turkish equivalence tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
