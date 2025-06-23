"""Kobo Anki add-on – core helper functions.

This module is **independent of Anki/Qt**; it can be imported from a plain
Python interpreter or test runner.
"""

from __future__ import annotations

import json
import os
import sqlite3
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache
from typing import List, Optional, Tuple

__all__ = [
    "normalise_word",
    "find_kobo_db",
    "get_kobo_wordlist",
    "fetch_definition",
]


# ---------------------------------------------------------------------------
# Pure helpers (no external runtime deps)
# ---------------------------------------------------------------------------

def normalise_word(word: str) -> str:  # noqa: D401 – simple verb
    """Return *word* in lowercase NFC form."""

    return unicodedata.normalize("NFC", word).lower()


def find_kobo_db() -> Optional[str]:
    """Locate `/Volumes/<VOL>/.kobo/KoboReader.sqlite` on macOS.

    Returns the first match or *None* if not found.
    """

    volumes_root = "/Volumes"
    if not os.path.isdir(volumes_root):
        return None

    for volume in os.listdir(volumes_root):
        potential = os.path.join(volumes_root, volume, ".kobo", "KoboReader.sqlite")
        if os.path.isfile(potential):
            return potential
    return None


def get_kobo_wordlist(db_path: str) -> list[tuple[str, str]]:
    """Read and normalise words from the Kobo **WordList** table.

    Returns a list of `(word, lang_code)` tuples, e.g., `[('apple', 'en')]`.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT Text, DictSuffix FROM WordList")
    rows = cursor.fetchall()
    connection.close()
    results = []
    for text, dict_suffix in rows:
        word = normalise_word(text)
        # DictSuffix is like '-en', '-de'; strip leading dash. Default to 'en'.
        lang = (dict_suffix or "-en").lstrip("-")
        results.append((word, lang))
    return results


# ---------------------------------------------------------------------------
# Online dictionary lookup (Kaikki.org only)
# ---------------------------------------------------------------------------

_KAikki_LANGUAGE_MAP = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
}


@lru_cache(maxsize=1024)
def fetch_definition(word: str, lang_code: str) -> str:
    """Return a short definition for *word* in its language from Kaikki.org."""
    word_lc = word.lower()
    lang_name = _KAikki_LANGUAGE_MAP.get(lang_code)
    if not lang_name:
        return ""  # Language not supported by our map

    first, first2 = word_lc[0], word_lc[:2]
    ka_url = (
        f"https://kaikki.org/dictionary/{lang_name}/meaning/"
        f"{first}/{first2}/{word_lc}.jsonl"
    )

    try:
        with urllib.request.urlopen(ka_url, timeout=5) as resp:
            if resp.status == 200:
                text_data = resp.read().decode('utf-8')
                # Parse JSON Lines format - each line is a separate JSON object
                lines = text_data.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "senses" in data:  # This line contains the main word data
                                glosses: list[str] = []
                                for sense in data.get("senses", []):
                                    g = sense.get("glosses") or sense.get("gloss")
                                    if g:
                                        glosses.extend(g if isinstance(g, list) else [str(g)])
                                if glosses:
                                    return "; ".join(dict.fromkeys(glosses))
                        except json.JSONDecodeError:
                            continue  # Skip malformed lines

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""  # Word not found, return empty string.
        raise  # For other HTTP errors, raise exception.
    except urllib.error.URLError:
        raise  # Re-raise network errors

    return ""  # nothing found 