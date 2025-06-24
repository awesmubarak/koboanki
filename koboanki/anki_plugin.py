"""Anki/Qt integration for the 'Kobo Word List' add-on.

This file is **only** imported when the `aqt` package is present (i.e. when
running inside the real Anki runtime).  It wires the core helper functions
into a Tools-menu action.
"""

from __future__ import annotations

import os

from aqt import mw  # type: ignore
from aqt.qt import QAction  # type: ignore
from aqt.utils import showInfo, tooltip  # type: ignore
from anki.notes import Note  # type: ignore

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


def get_deck_name():
    """Get the configured deck name for importing Kobo words.
    
    Returns:
        str: The deck name to use for imports
    """
    config = get_config()
    return config.get('deck_name', 'Kobo Vocabulary')


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
    """Callback for the menu action – fetch list and import words to Anki."""
    
    # Get user configuration
    deck_name = get_deck_name()
    
    # Find the Kobo database
    db_path = find_kobo_db()
    if not db_path:
        # Try the test database for development
        addon_module_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(addon_module_dir)
        test_db_path = os.path.join(project_root, "tests", "data", "TestKoboReader.sqlite")
        
        if os.path.isfile(test_db_path):
            db_path = test_db_path
            # Only show debug info if there are issues
            # showInfo(f"Using test database for development: {test_db_path}")
        else:
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

    # Get or create the deck
    deck_id = mw.col.decks.id(deck_name)
    
    # Find the note type (model) to use
    model_name = "Basic"  # Start with Anki's default Basic note type
    model = mw.col.models.by_name(model_name)
    if not model:
        # If Basic doesn't exist, use the first available model
        model = mw.col.models.all()[0]
        model_name = model['name']
    
    # Import the words
    added_count = 0
    skipped_count = 0
    added_words = []
    skipped_words = []
    
    for word, lang_code in words:
        # Create field data for this word
        fields = create_card_fields(word, lang_code)
        
        # Create a new note
        note = Note(mw.col, model)
        
        # Map our fields to the note type's fields
        # For Basic note type: Front and Back
        # For other note types: try to map intelligently
        model_fields = [f['name'] for f in model['flds']]
        
        if len(model_fields) >= 2:
            # Set the first field (usually "Front" or "Question")
            note.fields[0] = fields.get('Word', word)
            
            # Set the second field (usually "Back" or "Answer") 
            # Use our rich AllDefinitions content
            note.fields[1] = fields.get('AllDefinitions', fields.get('PrimaryDefinition', ''))
            
            # If there are more fields, try to fill them with relevant data
            for i, field_name in enumerate(model_fields[2:], start=2):
                if i < len(note.fields):
                    # Try to match field names to our data
                    if 'language' in field_name.lower():
                        note.fields[i] = lang_code
                    elif 'pronunciation' in field_name.lower() or 'ipa' in field_name.lower():
                        note.fields[i] = fields.get('Pronunciation', '')
                    elif 'etymology' in field_name.lower():
                        note.fields[i] = fields.get('Etymology', '')
                    elif 'example' in field_name.lower():
                        note.fields[i] = fields.get('Examples', '')
                    elif 'synonym' in field_name.lower():
                        note.fields[i] = fields.get('Synonyms', '')
        
        # Check if this note already exists (more robust duplicate check)
        # Search for notes in this deck that contain this exact word in the first field
        search_query = f'deck:"{deck_name}" {model_fields[0]}:"{word}"'
        existing = mw.col.find_notes(search_query)
        if existing:
            skipped_count += 1
            skipped_words.append(word)
            continue
            
        # Add the note to the collection
        try:
            mw.col.add_note(note, deck_id)
            added_count += 1
            added_words.append(word)
        except Exception as e:
            # If there's an error adding this specific note, skip it
            skipped_count += 1
            skipped_words.append(word)
            continue
    
    # Save changes
    mw.col.save()
    
    # Show completion message
    total_words = len(words)
    
    # Use HTML for rich text in the dialog
    message = f"""
Import complete for deck '<b>{deck_name}</b>'.<br>
Processed {total_words} words using note type '<b>{model_name}</b>'.
<hr>
"""

    if added_words:
        added_list = "".join(f"<li>{w}</li>" for w in sorted(added_words))
        message += f"""
<details>
    <summary><b>{len(added_words)} new cards added</b></summary>
    <ul style="list-style-type: none; padding-left: 1.2em; text-indent: -1.2em;">{added_list}</ul>
</details>
"""

    if skipped_words:
        skipped_list = "".join(f"<li>{w}</li>" for w in sorted(skipped_words))
        message += f"""
<details>
    <summary><b>{len(skipped_words)} words skipped</b> (already exist)</summary>
    <ul style="list-style-type: none; padding-left: 1.2em; text-indent: -1.2em;">{skipped_list}</ul>
</details>
"""
    
    showInfo(message)
    
    # Also show a quick tooltip
    if skipped_count > 0:
        tooltip(f"Added {added_count} new cards, skipped {skipped_count} duplicates")
    else:
        tooltip(f"Added {added_count} new cards to '{deck_name}'")


def create_anki_action() -> QAction:
    """Create the menu action for the Kobo import."""
    action = QAction("Import Words from Kobo", mw)
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