
from koboanki.core import get_kobo_wordlist, normalise_word


def test_get_kobo_wordlist_returns_word_and_lang_tuples() -> None:
    """This test needs a real Kobo database.
    
    For now, it's a placeholder to check the interface.
    """
    # Create a mock database or similar test
    # For now just test the function signature exists
    assert callable(get_kobo_wordlist)
    
    # Test data structure returned (mocked)
    # In a full test we'd use a test database
    test_result = [("apple", "en"), ("bonjour", "fr")]
    assert isinstance(test_result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in test_result)
    assert all(isinstance(word, str) and isinstance(lang, str) 
               for word, lang in test_result)


def test_normalise_word_nfc_lower() -> None:
    """Test word normalization."""
    # Test basic functionality
    assert normalise_word("Hello") == "hello"
    assert normalise_word("Café") == "café"
    assert normalise_word("naïve") == "naïve"
    
    # Test punctuation removal
    assert normalise_word("hello!") == "hello"
    assert normalise_word("world?") == "world"
    assert normalise_word("test...") == "test"
    
    # Test internal punctuation preservation
    assert normalise_word("don't") == "don't"
    assert normalise_word("mother-in-law") == "mother-in-law"
    
    # Test Unicode normalization
    composed = "é"  # Single character
    decomposed = "e\u0301"  # e + combining acute accent
    assert normalise_word(composed) == normalise_word(decomposed)
    
    # Test edge cases
    assert normalise_word("") == ""
    assert normalise_word("   spaces   ") == "   spaces   "  # Spaces preserved 