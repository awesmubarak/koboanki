"""Card builder with level-based templates.

This module implements the clean pipeline:
JSONL -> Python translator -> well-named fields -> HTML template

The translator converts WordData into level-appropriate field dictionaries,
and templates handle only presentation concerns.
"""

from __future__ import annotations

import html
import json
import os
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

from .core import WordData, WordSense, WordExample


class CardLevel(Enum):
    """Available card detail levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    FULL = "full"


@dataclass
class CardTemplate:
    """Template structure loaded from template files."""
    front: str
    back: str
    css: str


class CardBuilder:
    """Builds Anki card content from WordData using level-based templates."""
    
    def __init__(self, level: CardLevel = CardLevel.FULL):
        """Initialize with specified detail level."""
        self.level = level
        self._templates_cache = {}
        
    def build_fields(self, word_data: WordData) -> Dict[str, str]:
        """Convert WordData into level-appropriate field dictionary.
        
        Args:
            word_data: Rich word data from Kaikki API
            
        Returns:
            Dictionary of field names to values for Anki templates
        """
        # Start with base fields that all levels need
        fields = {
            "Word": self._escape_html(word_data.word),
            "Language": word_data.language,
        }
        
        # Add level-specific fields
        if self.level == CardLevel.BASIC:
            fields.update(self._build_basic_fields(word_data))
        elif self.level == CardLevel.INTERMEDIATE:
            fields.update(self._build_intermediate_fields(word_data))
        elif self.level == CardLevel.FULL:
            fields.update(self._build_full_fields(word_data))
            
        return fields
    
    def get_template(self) -> CardTemplate:
        """Load the template for the current level."""
        if self.level.value not in self._templates_cache:
            self._templates_cache[self.level.value] = self._load_template(self.level.value)
        return self._templates_cache[self.level.value]
    
    def _build_basic_fields(self, word_data: WordData) -> Dict[str, str]:
        """Build fields for basic level - just definitions."""
        return {
            "DefinitionList": self._format_simple_definitions(word_data),
            "HasDefinitions": "1" if word_data.senses else "",
        }
    
    def _build_intermediate_fields(self, word_data: WordData) -> Dict[str, str]:
        """Build fields for intermediate level - key facts with inline examples."""
        fields = {
            "PartOfSpeech": self._escape_html(word_data.part_of_speech or ""),
            "DefinitionList": self._format_detailed_definitions(word_data),
            "Synonyms": self._format_key_synonyms(word_data),
            "Pronunciation": self._format_primary_pronunciation(word_data),
            
            # Conditional flags
            "HasPartOfSpeech": "1" if word_data.part_of_speech else "",
            "HasDefinitions": "1" if word_data.senses else "",
            "HasSynonyms": "1" if word_data.synonyms else "",
            "HasPronunciation": "1" if word_data.pronunciation else "",
            
            # Empty fields for template compatibility
            "Examples": "",
            "HasExamples": "",
        }
        return fields
    
    def _build_full_fields(self, word_data: WordData) -> Dict[str, str]:
        """Build fields for full level - everything available."""
        fields = self._build_intermediate_fields(word_data)  # Start with intermediate
        
        # Add full-level exclusive content
        fields.update({
            "Etymology": self._format_etymology(word_data),
            "DerivedTerms": self._format_derived_terms(word_data),
            "AllExamples": self._format_all_examples(word_data),
            "AllSynonyms": self._format_all_synonyms(word_data),
            "Categories": self._format_categories(word_data),
            
            # Additional flags
            "HasEtymology": "1" if word_data.etymology_text else "",
            "HasDerivedTerms": "1" if word_data.derived else "",
            "HasCategories": "1" if word_data.categories else "",
        })
        
        # Override some intermediate fields with more detailed versions
        fields["DefinitionList"] = self._format_comprehensive_definitions(word_data)
        fields["Synonyms"] = self._format_all_synonyms(word_data)
        fields["Examples"] = self._format_all_examples(word_data)
        
        return fields
    
    def _format_simple_definitions(self, word_data: WordData) -> str:
        """Format basic numbered definition list."""
        if not word_data.senses:
            return ""
            
        definitions = []
        for i, sense in enumerate(word_data.senses[:3], 1):  # Limit to 3 for basic
            if sense.glosses:
                definition = self._escape_html(sense.glosses[0])  # Just first gloss
                definitions.append(f"<li>{definition}</li>")
        
        return "".join(definitions)
    
    def _format_detailed_definitions(self, word_data: WordData) -> str:
        """Format definitions with context tags and examples inline for intermediate level."""
        if not word_data.senses:
            return ""
            
        definitions = []
        for i, sense in enumerate(word_data.senses[:4], 1):  # Limit to 4 for intermediate
            if not sense.glosses:
                continue
                
            # Combine main glosses
            main_def = self._escape_html("; ".join(sense.glosses[:2]))  # Max 2 glosses per sense
            
            # Add context tags if available
            if sense.tags:
                context = ", ".join(sense.tags[:2])  # Max 2 tags
                main_def += f' <em>({self._escape_html(context)})</em>'
            
            definition_html = f"<li>{main_def}"
            
            # Add examples inline for intermediate level (1 example per sense max)
            if sense.examples:
                example = sense.examples[0]  # Just the first example
                text = example.text[:120] + "..." if len(example.text) > 120 else example.text
                example_html = f'<div class="example-inline">"{self._escape_html(text)}"</div>'
                definition_html += example_html
            
            definition_html += "</li>"
            definitions.append(definition_html)
        
        return "".join(definitions)
    
    def _format_comprehensive_definitions(self, word_data: WordData) -> str:
        """Format comprehensive definitions with examples inline."""
        if not word_data.senses:
            return ""
            
        definitions = []
        for i, sense in enumerate(word_data.senses, 1):
            if not sense.glosses:
                continue
                
            # Main definition with all glosses
            main_def = self._escape_html("; ".join(sense.glosses))
            
            # Add tags and categories
            contexts = []
            if sense.tags:
                contexts.extend(sense.tags[:3])
            if sense.categories:
                contexts.extend(sense.categories[:2])
                
            if contexts:
                context_str = ", ".join(contexts)
                main_def += f' <em>({self._escape_html(context_str)})</em>'
            
            definition_html = f"<li>{main_def}"
            
            # Add examples inline for full level
            if sense.examples:
                for example in sense.examples[:2]:  # Max 2 examples per sense
                    text = example.text[:100] + "..." if len(example.text) > 100 else example.text
                    example_html = f'<div class="example-inline">"{self._escape_html(text)}"</div>'
                    definition_html += example_html
            
            definition_html += "</li>"
            definitions.append(definition_html)
        
        return "".join(definitions)
    

    
    def _format_all_examples(self, word_data: WordData) -> str:
        """Format all examples for full level."""
        examples = []
        
        for sense in word_data.senses:
            for example in sense.examples[:3]:  # Max 3 per sense for full
                text = example.text[:150] + "..." if len(example.text) > 150 else example.text
                formatted = f'"{self._escape_html(text)}"'
                
                if example.reference:
                    ref = example.reference[:30] + "..." if len(example.reference) > 30 else example.reference
                    formatted += f" <small>—{self._escape_html(ref)}</small>"
                
                examples.append(formatted)
                
                if len(examples) >= 8:  # Overall limit for full level
                    break
            
            if len(examples) >= 8:
                break
        
        return "<br><br>".join(examples)
    
    def _format_key_synonyms(self, word_data: WordData) -> str:
        """Format 2-3 key synonyms for intermediate level."""
        if not word_data.synonyms:
            return ""
            
        synonyms = []
        for syn in word_data.synonyms[:3]:  # Limit for intermediate
            word = syn.get('word', '')
            if word:
                synonyms.append(f"<span class=\"synonym-item\">{self._escape_html(word)}</span>")
                
        return " • ".join(synonyms)
    
    def _format_all_synonyms(self, word_data: WordData) -> str:
        """Format all synonyms for full level."""
        if not word_data.synonyms:
            return ""
            
        synonyms = []
        for syn in word_data.synonyms[:8]:  # Reasonable limit
            word = syn.get('word', '')
            if not word:
                continue
                
            formatted = self._escape_html(word)
            
            # Add context tags for synonyms
            tags = syn.get('tags', [])
            if tags:
                context = ", ".join(tags[:2])
                formatted += f' <span class="sense">({self._escape_html(context)})</span>'
            
            synonyms.append(f"<li>{formatted}</li>")
                
        return "".join(synonyms)
    
    def _format_primary_pronunciation(self, word_data: WordData) -> str:
        """Format primary pronunciation for intermediate level."""
        if not word_data.pronunciation:
            return ""
            
        # Get the first/primary pronunciation
        pron = word_data.pronunciation[0]
        ipa = pron.get('ipa', '')
        if not ipa:
            return ""
            
        return f"/{self._escape_html(ipa)}/"
    
    def _format_etymology(self, word_data: WordData) -> str:
        """Format etymology for full level."""
        if not word_data.etymology_text:
            return ""
            
        etymology = word_data.etymology_text
        if len(etymology) > 200:
            etymology = etymology[:200] + "..."
            
        return self._escape_html(etymology)
    
    def _format_derived_terms(self, word_data: WordData) -> str:
        """Format derived terms for full level."""
        if not word_data.derived:
            return ""
            
        terms = []
        for term in word_data.derived[:10]:  # Reasonable limit
            word = term.get('word', '')
            if word:
                terms.append(f"<li>{self._escape_html(word)}</li>")
                
        return "".join(terms)
    
    def _format_categories(self, word_data: WordData) -> str:
        """Format categories for full level."""
        if not word_data.categories:
            return ""
            
        categories = [self._escape_html(cat) for cat in word_data.categories[:5]]
        return ", ".join(categories)
    
    def _has_examples(self, word_data: WordData) -> bool:
        """Check if any sense has examples."""
        return any(sense.examples for sense in word_data.senses)
    
    def _escape_html(self, text: str) -> str:
        """Safely escape HTML in text fields."""
        if not text:
            return ""
        return html.escape(text)
    
    def _load_template(self, level: str) -> CardTemplate:
        """Load template from template file."""
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        template_file = os.path.join(templates_dir, f"{level}.html")
        css_file = os.path.join(templates_dir, "card.css")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            return CardTemplate(
                front=template_data['front'],
                back=template_data['back'],
                css=css_content
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # Fallback to basic template if loading fails
            return CardTemplate(
                front="{{Word}}",
                back="{{DefinitionList}}",
                css=""
            )


# Convenience functions for the main module
def build_card_fields(word_data: WordData, level: CardLevel = CardLevel.FULL) -> Dict[str, str]:
    """Build card fields for the specified level."""
    builder = CardBuilder(level)
    return builder.build_fields(word_data)


def get_card_template(level: CardLevel = CardLevel.FULL) -> CardTemplate:
    """Get the template for the specified level."""
    builder = CardBuilder(level)
    return builder.get_template() 