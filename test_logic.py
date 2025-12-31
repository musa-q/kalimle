"""
Test script for game logic with new normalization rules
"""
from game.logic import normalize_arabic, validate_guess

def test_normalization():
    """Test that normalization works correctly"""
    print("=" * 60)
    print("Testing Arabic Normalization")
    print("=" * 60)

    # Test hamza/alif normalization - all should become ا
    test_cases = [
        ("أحمد", "احمد", "Alif with hamza above"),
        ("إسلام", "اسلام", "Alif with hamza below"),
        ("آمن", "امن", "Alif with madda"),
        ("ماء", "ماا", "Standalone hamza"),
        ("مؤمن", "مامن", "Hamza on waw"),
        ("شيئ", "شيا", "Hamza on yeh"),
        ("قرأ", "قرا", "Mixed hamza forms"),
    ]

    print("\n1. Hamza/Alif Normalization (all → ا):")
    for original, expected, description in test_cases:
        result = normalize_arabic(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {description}: '{original}' → '{result}' (expected: '{expected}')")

    # Test teh marbuta normalization
    print("\n2. Teh Marbuta Normalization (ة → ه):")
    teh_cases = [
        ("مدرسة", "مدرسه", "Word ending with teh marbuta"),
        ("قهوة", "قهوه", "Another teh marbuta example"),
    ]

    for original, expected, description in teh_cases:
        result = normalize_arabic(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {description}: '{original}' → '{result}' (expected: '{expected}')")

    # Test that ى (alif maqsura) stays DIFFERENT from ي (yeh)
    print("\n3. Alif Maqsura (ى) remains distinct from Yeh (ي):")
    ya_cases = [
        ("موسى", "موسى", "Alif maqsura should NOT change"),
        ("علي", "علي", "Normal yeh should NOT change"),
        ("على", "على", "Alif maqsura should NOT change to yeh"),
    ]

    for original, expected, description in ya_cases:
        result = normalize_arabic(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {description}: '{original}' → '{result}' (expected: '{expected}')")

    print("\n" + "=" * 60)


def test_game_logic():
    """Test the actual game validation logic"""
    print("\n" + "=" * 60)
    print("Testing Game Logic (validate_guess)")
    print("=" * 60)

    # Test 1: Exact match
    print("\n1. Exact Match Test:")
    target = "كتاب"
    guess = "كتاب"
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for tile in result:
        print(f"    '{tile['letter']}' → {tile['status']}")
    all_correct = all(tile['status'] == 'correct' for tile in result)
    print(f"  Result: {'✓ PASS' if all_correct else '✗ FAIL'}")

    # Test 2: Hamza variations should match
    print("\n2. Hamza Variation Test (أ vs ا):")
    target = "قرأ"  # Has hamza on alif
    guess = "قرا"   # Plain alif
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for tile in result:
        print(f"    '{tile['letter']}' → {tile['status']}")
    all_correct = all(tile['status'] == 'correct' for tile in result)
    print(f"  Result: {'✓ PASS - Hamza normalized!' if all_correct else '✗ FAIL'}")

    # Test 3: Reverse - plain alif in target, hamza in guess
    print("\n3. Reverse Hamza Test (ا vs أ):")
    target = "سماء"  # Plain alif, standalone hamza
    guess = "سماا"   # Plain alif instead of hamza
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for tile in result:
        print(f"    '{tile['letter']}' → {tile['status']}")
    all_correct = all(tile['status'] == 'correct' for tile in result)
    print(f"  Result: {'✓ PASS - Hamza normalized!' if all_correct else '✗ FAIL'}")

    # Test 4: Teh marbuta normalization
    print("\n4. Teh Marbuta Test (ة vs ه):")
    target = "قهوة"  # Teh marbuta
    guess = "قهوه"   # Regular heh
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for tile in result:
        print(f"    '{tile['letter']}' → {tile['status']}")
    all_correct = all(tile['status'] == 'correct' for tile in result)
    print(f"  Result: {'✓ PASS - Teh marbuta normalized!' if all_correct else '✗ FAIL'}")

    # Test 5: Alif maqsura should NOT match regular yeh
    print("\n5. Alif Maqsura Distinction Test (ى vs ي):")
    target = "موسى"  # Alif maqsura at end
    guess = "موسي"   # Regular yeh
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for tile in result:
        print(f"    '{tile['letter']}' → {tile['status']}")
    last_correct = result[-1]['status'] == 'correct'
    print(f"  Last letter status: {result[-1]['status']}")
    print(f"  Result: {'✗ FAIL - Should NOT match!' if last_correct else '✓ PASS - Correctly distinct!'}")

    # Test 6: Wrong position test
    print("\n6. Wrong Position Test:")
    target = "كتاب"
    guess = "بكات"
    result = validate_guess(guess, target)
    print(f"  Target: '{target}' | Guess: '{guess}'")
    for i, tile in enumerate(result):
        print(f"    Position {i}: '{tile['letter']}' → {tile['status']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_normalization()
    test_game_logic()
    print("\n✓ All tests completed!\n")
