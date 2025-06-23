# Kobo WordList table

This file documents the **WordList** table found in Kobo e-readers' `KoboReader.sqlite` database and explains which columns are used by the *koboanki* add-on.

## Location

```
.kobo/KoboReader.sqlite → table: WordList
```

## Schema

| Column       | Type | Notes |
|--------------|------|-------|
| `Text`       | TEXT (PK) | The looked-up word (normalised by Kobo) |
| `VolumeId`   | TEXT | File-url of the book where the lookup occurred (e.g. `file:///mnt/onboard/pg2680.epub`)|
| `DictSuffix` | TEXT | Two-letter dictionary suffix; `-en` for English, `-fr` for French, etc. |
| `DateCreated`| TEXT | ISO-8601 timestamp when the word was added to the list |

```sql
-- Inspect the schema yourself
PRAGMA table_info('WordList');
```
