import requests
import sqlite3
import threading
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo, qconnect
from os import path
from queue import Queue
import json
from PyQt5.QtWidgets import QFileDialog
from string import punctuation

### IO


def get_config() -> dict:
    """Opens and returns the config. TODO: link with the verifcation function."""
    config = mw.addonManager.getConfig(__name__)
    return config


def get_file_location() -> str:
    """Returns the kobo db file location. Empty if error or not found."""
    folder_name = QFileDialog.getExistingDirectory(
        None, "Select KOBO drive", path.expanduser("~"), QFileDialog.ShowDirsOnly
    )

    if folder_name:
        file_location = path.join(folder_name, ".kobo", "KoboReader.sqlite")
        if not (path.exists(file_location) and path.isfile(file_location)):
            showInfo(
                f"File path not found: {file_location}"
            )  # TODO: remove and use verificaction function
            file_location = ""
    else:
        file_location = ""

    return file_location


def get_kobo_wordlist(file_location: str) -> list:
    """Opens the kobo file and returns a list of saved words (normalised)."""
    connection = sqlite3.connect(file_location)
    cursor = connection.cursor()
    wordlist = [
        row[0] for row in cursor.execute("SELECT text from WordList").fetchall()
    ]
    normal_wordlist = [normalise_word(word) for word in wordlist]
    return normal_wordlist


def get_deck_dict() -> dict:
    """Gets the list of anki decks with some metadata."""
    deck_list = mw.col.decks.all_names_and_ids()
    deck_dict = {}
    for deck in deck_list:
        split_deck = str(deck).split("\n")
        id = split_deck[0].split(" ")[1]
        name = split_deck[1].split('"')[1]
        deck_dict[name] = id
    return deck_dict


def add_to_collection(word_defs: dict, deck_id: int) -> None:
    """Adds valid words to the collection"""
    working_words = {w: d for (w, d) in word_defs.items() if d}
    for word, definition in working_words.items():
        note = mw.col.newNote("Basic")  # type: ignore
        note["Front"] = word
        note["Back"] = definition
        note.tags.append("koboanki")
        # mw.col.addNote(note)
        mw.col.add_note(note, deck_id)  # type: ignore

    mw.col.save()
    return


### Acctual utils


def normalise_word(word: str) -> str:
    """Lowers the case of all characters and removes punctuation from the end of words."""
    return (word[:-1] + word[-1].strip(punctuation)).lower()


def get_link(word: str) -> str:
    """Creates a dictionary link from a language code and word."""
    return f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"


def filter_wordlist(kobo_wordlist: list, deck_id: int) -> list:
    """Returns a list of only words not already added to anki."""
    # TODO: return the duplicate items to show user at the end, alongside missing definitions

    deck_name = mw.col.decks.name_if_exists(deck_id)
    ids = mw.col.find_notes(f"deck:{deck_name}")

    anki_wordlist = [mw.col.getNote(id_).items()[0][1] for id_ in ids]
    new_wordlist = [word for word in kobo_wordlist if word not in anki_wordlist]

    return new_wordlist


def get_definitions(wordlist: list, lang: str) -> dict:
    """Concurently find defintions for all words"""
    # queue = Queue(maxsize=0)
    # num_theads = min(config["dl_threads"], len(wordlist))
    # definitions = [{} for _ in wordlist]
    # for i in range(len(wordlist)):
    #     queue.put((i, wordlist[i]))
    #
    # # create threads
    # for i in range(num_theads):
    #     worker = threading.Thread(
    #         target=queue_handler, args=(queue, definitions, config)
    #     )
    #     worker.setDaemon(True)
    #     worker.start()
    # queue.join()
    #
    # return {word: definition for word, definition in zip(wordlist, definitions)}
    def_dict = {}
    for word in wordlist:
        def_dict[word] = get_word_definition(word, "en")

    return def_dict


# def get_word_definition(word: str, lang: str, dl_timeout: int, n_retries: int) -> str:
# def get_word_definition(word: str, lang: str) -> str:
#     """Return the definition of a word that's passed to it. Empty if no defs."""
#     response = []
#     word_text = ""
#     try:
#         response = requests.get(get_link(word)).json()
#     except requests.exceptions.ConnectionError:  # TODO: raise errors in a clean way
#         response = "ERROR: no response"
#
#     word_text = str(response)[0]["meanings"] #TODO:
#
#     return word_text
def get_word_definition(word: str, language: str) -> str:
    """Return the definition of a word that's passed to it. Empty if no defs."""
    response = []
    word_text = ""
    try:
        response = requests.get(get_link(word)).json()
    except requests.exceptions.ConnectionError:
        return word_text

    try:
        for word_def in response:
            word_text = ""
            definition = ""

            phonetics = word_def["phonetics"]
            meanings = word_def["meanings"]

            phonetics = [phoenetic["text"] for phoenetic in phonetics]
            word_text = f"<small>{str(phonetics)}</small>"

            for meaning_n, meaning in enumerate(meanings):
                part_of_speech = meaning["partOfSpeech"]
                definition = meaning["definitions"][0]["definition"]
                example = meaning["definitions"][0]["example"]

                word_text += f"<br><b>{meaning_n+1}. </b> <small>{part_of_speech} - </small>{definition} <i> {example} </i>"

            # sometimes there's pronounciation info but not definition
            if definition == "":
                word_text = ""

    except:
        word_text = ""

    showInfo(word)
    showInfo(word_text)
    return word_text
