# CHANGELOG.md

## Unreleased

Added:

- Config field to specify number of download threads
- Timeouts to requests (with config option)
- Retries for failed connections (with config option)
- A blacklist for words not to look up

Changed:

- Relicensed to MIT
- Config file now has a few extra fields for the some the added features

Fixed:

- Wordlist now converted to lower case when pulled in from kobo

## 2.0.1 (2021-08-13)

Changed:

- Erroneous language codes will now be displayed in the popup

Fixed:

- Updated release script so the default config file is included in the release
- Will now exit on empty language code list
- Empty config files won't cause crashes (#6)

## 2.0.0 (2021-07-25)

Added:

- Threading!!! Up to 50 words can now be looked up at once, so adding words will be _much_ faster.
- Multilingual support for 13 languages!

Changed:

- The formatting of the notes is totally different now, with information on the pronounciation of the word, multiple definitions, and example text.

Fixed:

- Specify card type explicitly (#4)


## 1.1.0 (2021-05-31)

Fixed:

- Remove duplicate confirmation popups
- Improved error handling

## 1.0.0 (2021-05-30)

Features:

- Initial release!
