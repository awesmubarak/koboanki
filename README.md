# Koboanki v3 (work-in-progress)

TODO

## Enhanced Data Extraction

As of the enhanced version, koboanki now extracts comprehensive linguistic data:

### Basic Information
- **Word**: The looked-up term
- **Language**: Language code (en, de, fr, etc.)
- **Part of Speech**: noun, verb, adjective, etc.
- **Etymology**: Word origins and historical development

### Multiple Definitions (Senses)
- **Glosses**: Individual definitions for each meaning
- **Tags**: Context markers (e.g., "Internet", "biology", "archaic")
- **Categories**: Grammatical and topical classifications
- **Raw Glosses**: Unprocessed definition text with markup

### Usage Examples
- **Text**: Example sentences and quotes
- **Reference**: Citations and sources
- **Type**: Example type (quote, usage, etc.)

### Related Terms
- **Synonyms**: Alternative words with usage context
- **Hyponyms**: More specific terms (e.g., "fire ant" for "ant")
- **Derived Terms**: Related words (e.g., "anthill", "anteater")
- **Links**: Cross-references to related concepts

### Linguistic Details
- **Forms**: Plural, alternative spellings, inflections
- **Pronunciation**: IPA transcriptions, regional variants
- **Translations**: Equivalent terms in other languages

## API Functions

### Enhanced Extraction
```python
from koboanki.core import fetch_word_data, WordData

# Get comprehensive word data
word_data: WordData = fetch_word_data("ant", "en")

# Access rich information
print(word_data.part_of_speech)        # "noun"
print(word_data.etymology_text)        # Etymology information
print(len(word_data.senses))           # Number of definitions
print(word_data.senses[0].glosses)     # First definition
print(word_data.synonyms)              # List of synonyms
print(word_data.hyponyms)              # More specific terms
```

### Backward Compatible
```python
from koboanki.core import fetch_definition

# Simple string definition (legacy API)
definition: str = fetch_definition("ant", "en")
print(definition)  # "Any of various insects...; A Web spider"
```
