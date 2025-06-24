# Card Builder Pipeline Architecture

This document explains the new level-based card builder architecture implemented in KoboAnki v3.

## Overview

The new system implements a clean pipeline that separates data processing from presentation:

```
Kaikki JSONL → Python Translator → Well-Named Fields → HTML Template
```

This architecture provides three key benefits:
1. **Robustness**: API changes only affect the translator layer
2. **Maintainability**: Templates are pure HTML/CSS without data logic  
3. **Flexibility**: Easy to add new card levels or modify existing ones

## Architecture Components

### 1. Data Layer (`core.py`)

The `WordData`, `WordSense`, and `WordExample` dataclasses provide a stable interface to the rich linguistic data from the Kaikki API.

### 2. Translation Layer (`card_builder.py`)

The `CardBuilder` class translates rich `WordData` objects into level-appropriate field dictionaries.

#### Card Levels

Three levels of detail are supported:

- **BASIC**: Word + simple definitions only
- **INTERMEDIATE**: Adds part of speech, pronunciation, key examples, synonyms  
- **FULL**: Everything available (etymology, derived terms, categories, etc.)

### 3. Template Layer (`templates/`)

Pure HTML templates with Anki field placeholders:

```
templates/
├── basic.html        # Minimal card layout
├── intermediate.html # Balanced information
├── full.html        # Comprehensive details
└── card.css         # Shared styling
```

### 4. Integration Layer (`anki_plugin.py`)

The Anki plugin creates a custom note type "KoboAnki Word" with all necessary fields and uses the configured level to generate cards.

## Benefits

### For Users
- **Simple configuration**: Just choose basic/intermediate/full
- **Consistent cards**: All cards follow the same well-designed templates
- **Rich content**: Access to comprehensive linguistic data

### For Developers  
- **Clean separation**: Data logic separate from presentation
- **Easy testing**: Each layer can be tested independently
- **Simple maintenance**: Template changes don't require Python code changes
- **Extensible**: Adding new levels or fields is straightforward
