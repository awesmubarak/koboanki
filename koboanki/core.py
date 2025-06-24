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
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional, Tuple, Dict, Any
import re

__all__ = [
    "normalise_word",
    "find_kobo_db",
    "get_kobo_wordlist",
    "fetch_definition",
    "fetch_word_data",
    "WordData",
    "WordSense",
    "WordExample",
]


# ---------------------------------------------------------------------------
# Data structures for rich word information
# ---------------------------------------------------------------------------

@dataclass
class WordExample:
    """Represents a usage example of a word."""
    text: str
    reference: Optional[str] = None
    type: Optional[str] = None  # e.g., "quote", "example"


@dataclass
class WordSense:
    """Represents one meaning/sense of a word."""
    glosses: List[str] = field(default_factory=list)
    examples: List[WordExample] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    links: List[List[str]] = field(default_factory=list)  # Related terms
    raw_glosses: List[str] = field(default_factory=list)


@dataclass
class WordData:
    """Comprehensive word data from Kaikki API."""
    word: str
    language: str
    part_of_speech: Optional[str] = None
    senses: List[WordSense] = field(default_factory=list)
    synonyms: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    etymology_text: Optional[str] = None
    pronunciation: List[Dict[str, Any]] = field(default_factory=list)  # IPA, audio, etc.
    hyponyms: List[Dict[str, Any]] = field(default_factory=list)  # More specific terms
    derived: List[Dict[str, Any]] = field(default_factory=list)  # Derived terms
    categories: List[str] = field(default_factory=list)  # Top-level categories
    translations: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_primary_definition(self) -> str:
        """Get the first definition for backward compatibility."""
        if self.senses and self.senses[0].glosses:
            return self.senses[0].glosses[0]
        return ""
    
    def get_all_definitions(self) -> List[str]:
        """Get all definitions across all senses."""
        definitions = []
        for sense in self.senses:
            definitions.extend(sense.glosses)
        return definitions
    
    def get_simple_definition(self) -> str:
        """Get definitions formatted like the old function for compatibility."""
        all_defs = self.get_all_definitions()
        return "; ".join(dict.fromkeys(all_defs)) if all_defs else ""


# ---------------------------------------------------------------------------
# Pure helpers (no external runtime deps)
# ---------------------------------------------------------------------------

def normalise_word(word: str) -> str:  # noqa: D401 – simple verb
    """Return *word* in lowercase NFC form with trailing punctuation removed."""
    # First normalize and convert to lowercase
    normalized = unicodedata.normalize("NFC", word).lower()
    
    # Strip punctuation from the end, but preserve hyphens and apostrophes within words
    # This regex removes trailing punctuation but keeps internal punctuation
    cleaned = re.sub(r'[^\w\s\'-]+$', '', normalized)
    
    return cleaned


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
def fetch_word_data(word: str, lang_code: str) -> Optional[WordData]:
    """Fetch comprehensive word data from Kaikki.org API.
    
    Returns a WordData object with all available linguistic information,
    or None if the word is not found or language is not supported.
    """
    word_lc = word.lower()
    lang_name = _KAikki_LANGUAGE_MAP.get(lang_code)
    if not lang_name:
        return None  # Language not supported

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
                                return _parse_word_data(data, word, lang_code)
                        except json.JSONDecodeError:
                            continue  # Skip malformed lines

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # Word not found
        raise  # For other HTTP errors, raise exception
    except urllib.error.URLError:
        raise  # Re-raise network errors

    return None  # nothing found


def _parse_word_data(data: Dict[str, Any], word: str, lang_code: str) -> WordData:
    """Parse the JSON data from Kaikki API into a WordData object."""
    word_data = WordData(word=word, language=lang_code)
    
    # Extract basic information
    word_data.part_of_speech = data.get("pos")
    word_data.etymology_text = data.get("etymology_text")
    word_data.categories = data.get("categories", [])
    
    # Extract forms (plural, alternatives, etc.)
    word_data.forms = data.get("forms", [])
    
    # Extract synonyms
    word_data.synonyms = data.get("synonyms", [])
    
    # Extract hyponyms (more specific terms)
    word_data.hyponyms = data.get("hyponyms", [])
    
    # Extract derived terms
    word_data.derived = data.get("derived", [])
    
    # Extract pronunciation data
    word_data.pronunciation = data.get("sounds", [])
    
    # Extract translations
    word_data.translations = data.get("translations", [])
    
    # Extract senses (definitions)
    for sense_data in data.get("senses", []):
        sense = WordSense()
        
        # Extract glosses (definitions)
        glosses = sense_data.get("glosses", [])
        if glosses:
            sense.glosses = glosses if isinstance(glosses, list) else [str(glosses)]
        
        # Extract raw glosses
        raw_glosses = sense_data.get("raw_glosses", [])
        if raw_glosses:
            sense.raw_glosses = raw_glosses if isinstance(raw_glosses, list) else [str(raw_glosses)]
        
        # Extract categories and tags
        sense.categories = sense_data.get("categories", [])
        sense.tags = sense_data.get("tags", [])
        
        # Extract links (related terms)
        sense.links = sense_data.get("links", [])
        
        # Extract examples
        for example_data in sense_data.get("examples", []):
            example = WordExample(
                text=example_data.get("text", ""),
                reference=example_data.get("ref"),
                type=example_data.get("type")
            )
            sense.examples.append(example)
        
        word_data.senses.append(sense)
    
    return word_data


@lru_cache(maxsize=1024)
def fetch_definition(word: str, lang_code: str) -> str:
    """Return a short definition for *word* in its language from Kaikki.org.
    
    This function maintains backward compatibility with the original API.
    For richer data, use fetch_word_data() instead.
    """
    word_data = fetch_word_data(word, lang_code)
    if word_data:
        return word_data.get_simple_definition()
    return "" 