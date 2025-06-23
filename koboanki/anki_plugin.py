"""Anki/Qt integration for the 'Kobo Word List' add-on.

This file is **only** imported when the `aqt` package is present (i.e. when
running inside the real Anki runtime).  It wires the core helper functions
into a Tools-menu action.
"""

from __future__ import annotations

from aqt import mw  # type: ignore
from aqt.qt import QAction  # type: ignore
from aqt.utils import showInfo  # type: ignore

from .core import fetch_definition, find_kobo_db, get_kobo_wordlist


def _run_import() -> None:
    """Callback for the menu action – fetch list, show popup."""

    db_location = find_kobo_db()
    if not db_location:
        showInfo("Could not locate KOBO database under /Volumes.")
        return

    wordlist_with_langs = get_kobo_wordlist(db_location)
    if not wordlist_with_langs:
        showInfo("No words found in WordList table.")
        return

    lines: list[str] = []
    for word, lang in wordlist_with_langs:
        definition = fetch_definition(word, lang)
        lines.append(f"{word} ({lang}): {definition}")

    showInfo("\n".join(lines))


def setup() -> None:
    """Register Tools ▸ Import Kobo Word List action."""

    action = QAction("Import Kobo Word List", mw)
    action.triggered.connect(_run_import)
    mw.form.menuTools.addAction(action) 