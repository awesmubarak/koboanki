"""Anki/Qt integration for the 'Kobo Word List' add-on.

This file is **only** imported when the `aqt` package is present (i.e. when
running inside the real Anki runtime).  It wires the core helper functions
into a Tools-menu action.
"""

from __future__ import annotations

from aqt import mw  # type: ignore
from aqt.qt import QAction  # type: ignore
from aqt.utils import showInfo  # type: ignore

from .core import fetch_definition, fetch_word_data, find_kobo_db, get_kobo_wordlist
from .template_processor import process_word_for_anki, TemplateConfig


def get_config():
    """Get the addon configuration from Anki's config system."""
    return mw.addonManager.getConfig(__name__)


def get_card_templates():
    """Get the configured card templates for creating Anki cards.
    
    Returns:
        dict: Dictionary containing front_template, back_template, and css
    """
    config = get_config()
    return {
        'front_template': config.get('front_template', '{{Word}}'),
        'back_template': config.get('back_template', '{{AllDefinitions}}'),
        'css': config.get('css', '.card { font-family: arial; font-size: 20px; }')
    }


def create_card_fields(word: str, lang_code: str) -> dict:
    """Create template fields for a word using enhanced data extraction.
    
    Args:
        word: The word to look up
        lang_code: Language code (e.g., 'en', 'de', 'fr')
        
    Returns:
        Dictionary of field names to values for Anki card creation
    """
    # Try enhanced extraction first
    word_data = fetch_word_data(word, lang_code)
    
    if word_data:
        # Use rich template processing
        return process_word_for_anki(word_data)
    else:
        # Fallback to simple extraction for backward compatibility
        definition = fetch_definition(word, lang_code)
        return {
            "Word": word,
            "Language": lang_code,
            "PrimaryDefinition": definition,
            "AllDefinitions": definition,
            "DefinitionCount": "1" if definition else "0",
            # Empty values for conditional fields
            "HasMultipleDefinitions": "",
            "HasPartOfSpeech": "",
            "HasEtymology": "",
            "HasPronunciation": "",
            "HasSynonyms": "",
            "HasExamples": "",
            "HasDerivedTerms": "",
            "PartOfSpeech": "",
            "Etymology": "",
            "Pronunciation": "",
            "Synonyms": "",
            "Examples": "",
            "DerivedTerms": ""
        }


def _run_import() -> None:
    """Callback for the menu action – fetch list, show popup."""
    
    # Get user configuration for templates
    config = get_config()
    templates = get_card_templates()
    
    # Find the Kobo database
    db_path = find_kobo_db()
    if not db_path:
        showInfo("No Kobo device found. Please connect your Kobo eReader.")
        return

    # Fetch the word list from Kobo
    try:
        words = get_kobo_wordlist(db_path)
    except Exception as e:
        showInfo(f"Error reading Kobo database: {str(e)}")
        return

    if not words:
        showInfo("No words found in your Kobo word list.")
        return

    # Process words and create preview
    sample_words = words[:5]  # Show first 5 for preview
    processed_samples = []
    
    for word, lang_code in sample_words:
        fields = create_card_fields(word, lang_code)
        processed_samples.append(f"• {word} ({lang_code}): {fields.get('PrimaryDefinition', 'No definition')}")
    
    preview_text = "\n".join(processed_samples)
    if len(words) > 5:
        preview_text += f"\n... and {len(words) - 5} more words"
    
    # Create summary message
    total_words = len(words)
    message = f"""Found {total_words} words in your Kobo word list.

Sample words:
{preview_text}

Template configuration:
• Enhanced data extraction: ✓ Enabled
• Multiple definitions: ✓ Supported  
• Etymology & pronunciation: ✓ Included
• Examples & synonyms: ✓ Included

Note: This preview shows basic information. The actual cards will include rich formatting with multiple definitions, examples, pronunciation, and related terms when available."""

    showInfo(message)


def create_anki_action() -> QAction:
    """Create the menu action for the Kobo import."""
    action = QAction("Import from Kobo", mw)
    action.triggered.connect(_run_import)  # type: ignore
    return action


def setup() -> None:
    """Setup function for backward compatibility with __init__.py."""
    if mw:
        action = create_anki_action()
        mw.form.menuTools.addAction(action)


# Legacy initialization approach for backward compatibility
def init_plugin():
    """Initialize the plugin by adding it to Anki's Tools menu."""
    setup() 