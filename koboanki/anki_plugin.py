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


def get_config():
    """Get the addon configuration from Anki's config system."""
    return mw.addonManager.getConfig(__name__)


def get_card_templates():
    """Get the configured card templates for creating Anki cards.
    
    Returns:
        dict: Dictionary containing front_template, back_template, and css
    """
    config = get_config()
    if not config:
        # Fallback defaults if config is not available
        return {
            "front_template": "{{Word}}",
            "back_template": "{{Definition}}<br><br>Language: {{Language}}",
            "css": ".card { font-family: arial; font-size: 20px; text-align: center; }"
        }
    
    return {
        "front_template": config.get("front_template", "{{Word}}"),
        "back_template": config.get("back_template", "{{Definition}}<br><br>Language: {{Language}}"),
        "css": config.get("css", ".card { font-family: arial; font-size: 20px; text-align: center; }")
    }


def _run_import() -> None:
    """Callback for the menu action – fetch list, show popup."""
    
    # Get user configuration for templates
    config = get_config()
    
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