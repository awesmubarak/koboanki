# Kaikki.org Dictionary API

This file documents the **Kaikki.org** dictionary API used by the *koboanki* add-on to fetch word definitions.

## API Endpoint

```
https://kaikki.org/dictionary/{Language}/meaning/{first_letter}/{first_two_letters}/{word}.jsonl
```

**Example**: `https://kaikki.org/dictionary/English/meaning/a/ap/apple.jsonl`

## Supported Languages

| Code | Language | Kaikki Name |
|------|----------|-------------|
| `en` | English | `English` |
| `de` | German | `German` |
| `fr` | French | `French` |
| `es` | Spanish | `Spanish` |
| `it` | Italian | `Italian` |
| `pt` | Portuguese | `Portuguese` |
| `nl` | Dutch | `Dutch` |
| `sv` | Swedish | `Swedish` |
| `da` | Danish | `Danish` |
| `no` | Norwegian | `Norwegian` |
| `fi` | Finnish | `Finnish` |

## Response Format

- **Format**: JSON Lines (`.jsonl`) - each line is a separate JSON object
- **Data**: Extracts `glosses` from `senses` fields, joined with semicolons
- **404**: Word not found (returns empty string)
- **Cache**: LRU cache with 128 entries to avoid redundant API calls

```python
# Example response parsing
"A round fruit; A technology company"
``` 