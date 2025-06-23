"""Template processing and data formatting for Anki cards.

This module converts rich WordData objects into template-friendly field dictionaries
that work with Anki's native conditional templating system.
"""

from __future__ import annotations

import html
from typing import Dict, List, Optional
from dataclasses import dataclass

from .core import WordData, WordSense, WordExample


@dataclass
class TemplateConfig:
    """Configuration for template processing."""
    max_definitions: int = 3
    max_examples: int = 2
    max_synonyms: int = 5
    max_derived_terms: int = 5
    etymology_max_length: int = 200
    example_max_length: int = 150
    include_pronunciation: bool = True
    include_etymology: bool = True
    include_examples: bool = True
    include_synonyms: bool = True
    include_derived_terms: bool = True


class TemplateProcessor:
    """Processes WordData into Anki-compatible template fields."""
    
    def __init__(self, config: Optional[TemplateConfig] = None):
        """Initialize with optional configuration."""
        self.config = config or TemplateConfig()
    
    def process_word_data(self, word_data: WordData) -> Dict[str, str]:
        """Convert WordData into template-friendly fields.
        
        Args:
            word_data: Rich word data from the API
            
        Returns:
            Dictionary of field names to values for use in Anki templates
        """
        fields = {
            # Basic fields
            "Word": self._escape_html(word_data.word),
            "Language": word_data.language,
            "PartOfSpeech": self._escape_html(word_data.part_of_speech or ""),
            
            # Definition fields
            "PrimaryDefinition": self._get_primary_definition(word_data),
            "AllDefinitions": self._format_all_definitions(word_data),
            "DefinitionCount": str(len(word_data.senses)),
            
            # Conditional flags
            "HasMultipleDefinitions": "1" if len(word_data.senses) > 1 else "",
            "HasPartOfSpeech": "1" if word_data.part_of_speech else "",
            "HasEtymology": "1" if (word_data.etymology_text and self.config.include_etymology) else "",
            "HasPronunciation": "1" if (word_data.pronunciation and self.config.include_pronunciation) else "",
            "HasSynonyms": "1" if (word_data.synonyms and self.config.include_synonyms) else "",
            "HasExamples": "1" if (self._has_examples(word_data) and self.config.include_examples) else "",
            "HasDerivedTerms": "1" if (word_data.derived and self.config.include_derived_terms) else "",
        }
        
        # Add optional content fields (always include fields for template compatibility)
        fields["Etymology"] = self._format_etymology(word_data) if self.config.include_etymology else ""
        fields["Pronunciation"] = self._format_pronunciation(word_data) if self.config.include_pronunciation else ""
        fields["Examples"] = self._format_examples(word_data) if self.config.include_examples else ""
        fields["Synonyms"] = self._format_synonyms(word_data) if self.config.include_synonyms else ""
        fields["DerivedTerms"] = self._format_derived_terms(word_data) if self.config.include_derived_terms else ""
            
        return fields
    
    def _escape_html(self, text: str) -> str:
        """Safely escape HTML in text fields."""
        if not text:
            return ""
        return html.escape(text)
    
    def _get_primary_definition(self, word_data: WordData) -> str:
        """Get the first definition for simple display."""
        if word_data.senses and word_data.senses[0].glosses:
            return self._escape_html(word_data.senses[0].glosses[0])
        return ""
    
    def _format_all_definitions(self, word_data: WordData) -> str:
        """Format all definitions with numbers and context."""
        if not word_data.senses:
            return ""
            
        definitions = []
        for i, sense in enumerate(word_data.senses[:self.config.max_definitions], 1):
            if not sense.glosses:
                continue
                
            # Combine glosses for this sense
            glosses = "; ".join(sense.glosses)
            definition = self._escape_html(glosses)
            
            # Add tags if present
            if sense.tags:
                tags = ", ".join(sense.tags[:3])  # Limit tags
                definition += f' <em>({self._escape_html(tags)})</em>'
            
            definitions.append(f"{i}. {definition}")
        
        return "<br><br>".join(definitions)
    
    def _format_etymology(self, word_data: WordData) -> str:
        """Format etymology information."""
        if not word_data.etymology_text:
            return ""
            
        etymology = word_data.etymology_text
        if len(etymology) > self.config.etymology_max_length:
            etymology = etymology[:self.config.etymology_max_length] + "..."
            
        return self._escape_html(etymology)
    
    def _format_pronunciation(self, word_data: WordData) -> str:
        """Format pronunciation information."""
        if not word_data.pronunciation:
            return ""
            
        pronunciations = []
        for pron in word_data.pronunciation[:3]:  # Limit to 3 variants
            ipa = pron.get('ipa', '')
            if not ipa:
                continue
                
            # Add variant tags if present
            tags = pron.get('tags', [])
            if tags:
                variant = f" <small>({', '.join(tags[:2])})</small>"
            else:
                variant = ""
                
            pronunciations.append(f"{self._escape_html(ipa)}{variant}")
        
        return "<br>".join(pronunciations)
    
    def _has_examples(self, word_data: WordData) -> bool:
        """Check if any sense has examples."""
        return any(sense.examples for sense in word_data.senses)
    
    def _format_examples(self, word_data: WordData) -> str:
        """Format usage examples."""
        if not self.config.include_examples:
            return ""
            
        examples = []
        examples_found = 0
        
        for sense in word_data.senses:
            if examples_found >= self.config.max_examples:
                break
                
            for example in sense.examples:
                if examples_found >= self.config.max_examples:
                    break
                    
                text = example.text
                if len(text) > self.config.example_max_length:
                    text = text[:self.config.example_max_length] + "..."
                
                formatted = f'"{self._escape_html(text)}"'
                
                # Add reference if available
                if example.reference:
                    ref = example.reference
                    if len(ref) > 50:  # Truncate long references
                        ref = ref[:50] + "..."
                    formatted += f" <small>—{self._escape_html(ref)}</small>"
                
                examples.append(formatted)
                examples_found += 1
        
        return "<br><br>".join(examples)
    
    def _format_synonyms(self, word_data: WordData) -> str:
        """Format synonyms list."""
        if not word_data.synonyms:
            return ""
            
        synonyms = []
        for syn in word_data.synonyms[:self.config.max_synonyms]:
            word = syn.get('word', '')
            if not word:
                continue
                
            formatted = self._escape_html(word)
            
            # Add tags for context (e.g., archaic, informal)
            tags = syn.get('tags', [])
            if tags:
                context = ", ".join(tags[:2])  # Limit to 2 tags
                formatted += f" <small>({self._escape_html(context)})</small>"
            
            synonyms.append(formatted)
        
        return ", ".join(synonyms)
    
    def _format_derived_terms(self, word_data: WordData) -> str:
        """Format derived terms list."""
        if not word_data.derived:
            return ""
            
        terms = []
        for derived in word_data.derived[:self.config.max_derived_terms]:
            word = derived.get('word', '')
            if word:
                terms.append(self._escape_html(word))
        
        return ", ".join(terms)


def get_default_processor() -> TemplateProcessor:
    """Get a template processor with default configuration."""
    return TemplateProcessor()


def process_word_for_anki(word_data: WordData, config: Optional[TemplateConfig] = None) -> Dict[str, str]:
    """Convenience function to process word data for Anki templates.
    
    Args:
        word_data: Rich word data from the API
        config: Optional template configuration
        
    Returns:
        Dictionary of field names to values ready for Anki templates
    """
    processor = TemplateProcessor(config)
    return processor.process_word_data(word_data) 