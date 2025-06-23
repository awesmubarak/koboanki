import pathlib

from koboanki.core import get_kobo_wordlist, normalise_word


def test_get_kobo_wordlist_returns_word_and_lang_tuples():
    """Verify the helper reads all words and their language codes.

    - Words should be normalised (lowercase, NFC).
    - Language codes should be stripped of the leading dash (e.g., '-en' -> 'en').
    """
    db_path = pathlib.Path(__file__).parent / "data" / "TestKoboReader.sqlite"
    results = get_kobo_wordlist(str(db_path))

    # Convert list of tuples to a dict for easier assertion
    result_map = dict(results)

    assert len(result_map) == 10
    assert result_map["apple"] == "en"
    assert result_map["zargle"] == "en"
    assert result_map["apfel"] == "de"
    assert result_map["philosophie"] == "de"
    assert result_map["blurfisch"] == "de"

    # Check the whole set to be sure
    expected = {
        ("apple", "en"),
        ("philosophy", "en"),
        ("banana", "en"),
        ("zargle", "en"),
        ("blurf", "en"),
        ("apfel", "de"),
        ("philosophie", "de"),
        ("banane", "de"),
        ("zargeln", "de"),
        ("blurfisch", "de"),
    }
    assert set(results) == expected


def test_normalise_word_nfc_lower():
    """Sanity-check the normalisation function."""
    assert normalise_word("Äpfel") == "äpfel"
    assert normalise_word("CAFÉ") == "café" 