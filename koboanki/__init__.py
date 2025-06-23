# mypy: disable-error-code="import-not-found"
from __future__ import annotations

from aqt import mw  # type: ignore
from aqt.utils import showInfo  # type: ignore
from aqt.qt import QAction  # type: ignore

# Standard-library imports
import os
import sqlite3
import unicodedata
from typing import List, Optional


# ------------------------------------------------------------
# Kobo helper functions (no external dependencies)
# ------------------------------------------------------------


def normalise_word(word: str) -> str:
    """Return the word in lowercase NFC form."""

    return unicodedata.normalize("NFC", word).lower()


def find_kobo_db() -> Optional[str]:
    """Locate /Volumes/<VOL>/.kobo/KoboReader.sqlite on macOS."""

    volumes_root = "/Volumes"
    if not os.path.isdir(volumes_root):
        return None

    for volume in os.listdir(volumes_root):
        potential = os.path.join(volumes_root, volume, ".kobo", "KoboReader.sqlite")
        if os.path.isfile(potential):
            return potential
    return None


def get_kobo_wordlist(db_path: str) -> List[str]:
    """Read and normalise words from the Kobo WordList table."""

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT text FROM WordList")
    words = [row[0] for row in cursor.fetchall()]
    connection.close()
    return [normalise_word(w) for w in words]


def testFunction() -> None:
    """Triggered from the Tools ▸ test menu-item.

    Finds the Kobo database automatically, prints all words to the console, and
    shows a short message when done.
    """

    db_location = find_kobo_db()
    if not db_location:
        showInfo("Could not locate KOBO database under /Volumes.")
        return

    wordlist = get_kobo_wordlist(db_location)

    # Show all words in a single popup message (one per line)
    if wordlist:
        showInfo("\n".join(wordlist))
    else:
        showInfo("No words found in WordList table.")


action = QAction("Import Kobo Word List", mw)
action.triggered.connect(testFunction)
mw.form.menuTools.addAction(action) 