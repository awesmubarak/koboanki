import pathlib

from koboanki import get_kobo_wordlist, normalise_word


def test_get_kobo_wordlist_reads_all_words():
    """The helper should return *all* words present in the test fixture DB
    and normalise them to lowercase NFC.
    """

    db_path = pathlib.Path(__file__).parent / "data" / "TestKoboReader.sqlite"
    words = get_kobo_wordlist(str(db_path))

    expected = {
        "apple",
        "philosophy",
        "banana",
        "zargle",
        "blurf",
        "apfel",
        "philosophie",
        "banane",
        "zargeln",
        "blurfisch",
    }

    assert set(words) == expected
    assert len(words) == 10


def test_normalise_word_nfc_lower():
    assert normalise_word("Äpfel") == "äpfel"  # sanity check NFC + lowercase 