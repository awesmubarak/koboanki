# KoboAnki

An Anki add-on to import your vocabulary from your Kobo eReader.

---

This add-on connects directly to your Kobo device, fetches your saved word list, and enriches it with detailed definitions, pronunciations, and example sentences before adding them to a dedicated Anki deck.

## Features

-   **Automatic Kobo Detection**: Just plug in your Kobo eReader, and the add-on will find it automatically.
-   **Rich Word Data**: Goes beyond simple definitions by fetching detailed data including part of speech, etymology, phonetic pronunciations, and synonyms.
-   **Example Sentences**: Automatically includes example sentences for each word to provide context.
-   **Customisable Card Templates**: Choose from three levels of card detail to match your learning style:
    -   **Basic**: Word and definition.
    -   **Intermediate**: Adds part of speech, pronunciation, and examples.
    -   **Full**: Includes everything: etymology, synonyms, derived terms, and more.
-   **Duplicate Prevention**: Intelligently skips words that are already in your Anki deck.
-   **Detailed Import Summary**: Get a clear report of which words were added, skipped, or failed to import.

## Installation

1.  Go to the Anki Add-ons dialog: **Tools -> Add-ons**.
2.  Click **"Get Add-ons..."** and paste the following code: `1642554232`
3.  Restart Anki.

## Usage

1.  Connect your Kobo eReader to your computer.
2.  In Anki, go to **Tools -> Import Words from Kobo**.
3.  The add-on will scan your device, process the words, and import them into a new deck called "Kobo Vocabulary".
4.  A summary will appear showing the results of the import.

## Configuration

You can customize the add-on's behavior by editing the configuration file.

1.  In Anki, go to **Tools -> Add-ons**.
2.  Select "KoboAnki" from the list and click the **"Config"** button.
3.  You can change the following settings:
    -   `deck_name`: The name of the deck where new cards will be created (default: `"Kobo Vocabulary"`).
    -   `card_level`: The level of detail for new cards. Options are `"basic"`, `"intermediate"`, or `"full"` (default: `"intermediate"`).

```json
{
  "deck_name": "Kobo Vocabulary",
  "card_level": "intermediate"
}
```

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
