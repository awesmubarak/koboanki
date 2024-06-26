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


def get_blacklist() -> list:
    """Opens and normalises the blacklist. TODO: create blacklist if there isn't one."""
    user_files_dir = path.join(mw.pm.addonFolder(), "koboanki", "user_files")
    with open(path.join(user_files_dir, "blacklist.json")) as file:
        blacklist = json.load(file)
    normal_blacklist = [normalise_word(word) for word in blacklist]
    return normal_blacklist


def try_link(link) -> bool:
    """Verifies if a link is valid. Unvalid links don't connect or 404."""
    valid = True
    try:
        response = requests.get(link)
        if response.status_code == 404:
            valid = False
    except requests.exceptions.ConnectionError:
        valid = False

    return valid


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


### Verification
# TODO


def verify_config(config: dict) -> bool:
    if not config:
        showInfo("Config file is empty")
        return False
    if not "language_list" in config:
        showInfo("Config file does not contain a language list")
        return False
    if len(config["language_list"]) == 0:
        showInfo("Language list is empty")
        return False

    links = {code: get_link(code, "test") for code in config["language_list"]}
    links_statuses = {code: try_link(link) for code, link in links.items()}
    failed_codes = [code for code, status in links_statuses.items() if not status]
    if failed_codes:
        showInfo(f"The following language codes are not valid: {failed_codes}")
        return False
    return True


### Interfaces


def get_words():
    """Calls all functions. Gets words."""

    blacklist = get_blacklist()
    if not blacklist:
        showInfo("No valid blacklist found")
        return

    # get folder name
    # TODO: this is temporary, gets rid of file opener and replaces it with list of pre-determined words. Doesn't need kobo plugged in.
    # file_location = get_file_location()
    # if not file_location:
    #     return
    #
    # # read in the word list
    # wordlist = get_kobo_wordlist(file_location)
    # if not wordlist:
    #     showInfo("No saved words found")
    #     return
    wordlist = ["Test", "thistle", "guitarrrrrrrrr", "grün", "درخت"]

    # check internet connection
    # if not try_link(get_link("en_US", "test")):
    #     showInfo("Can't access server, faulty internet connection?")
    #     return

    # find newwords, get definitions, add to collection
    # new_wordlist = get_new_wordlist(wordlist)
    # not_blacklisted = [word for word in new_wordlist if word not in blacklist]
    word_defs = get_definitions(wordlist, "en")

    return word_defs


### Acctual utils


def normalise_word(word: str) -> str:
    """Lowers the case of all characters and removes punctuation from the end of words."""
    return (word[:-1] + word[-1].strip(punctuation)).lower()


def get_link(language_code: str, word: str) -> str:
    """Creates a dictionary link from a language code and word."""
    return f"https://api.dictionaryapi.dev/api/v2/entries/{language_code}/{word}"


def get_new_wordlist(kobo_wordlist: list) -> list:
    """Returns a list of only words not already added to anki."""
    # TODO: this should look in the current deck. commenting out for now.
    # ids = mw.col.find_notes("")
    # anki_wordlist = [mw.col.getNote(id_).items()[0][1] for id_ in ids]
    # new_wordlist = [word for word in kobo_wordlist if word not in anki_wordlist]
    # # new_wordlist = ["hi", "hello", "bye", "test", "double", "triple"]
    # return new_wordlist
    return kobo_wordlist


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
def get_word_definition(word: str, lang: str) -> str:
    """Return the definition of a word that's passed to it. Empty if no defs."""
    # response = []
    # word_text = ""
    # try:
    #     response = requests.get(get_link(lang, word), timeout=dl_timeout).json()
    # except requests.exceptions.ConnectionError:  # TODO: test this
    #     if n_retries > 1:
    #         word_text = get_word_definition(word, lang, dl_timeout, n_retries - 1)
    #     else:
    #         response = ""
    #     return word_text
    #
    # try:
    #     for word_def in response:
    #         word_text = ""
    #         definition = ""
    #
    #         phonetics = word_def["phonetics"]
    #         meanings = word_def["meanings"]
    #
    #         phonetics = [phoenetic["text"] for phoenetic in phonetics]
    #         word_text = f"<small>{str(phonetics)}</small>"
    #
    #         for meaning_n, meaning in enumerate(meanings):
    #             part_of_speech = meaning["partOfSpeech"]
    #             definition = meaning["definitions"][0]["definition"]
    #             example = meaning["definitions"][0]["example"]
    #
    #             word_text += f"<br><b>{meaning_n+1}. </b> <small>{part_of_speech} - </small>{definition} <i> {example} </i>"
    #
    #         # sometimes there's pronounciation info but not definition
    #         if definition == "":
    #             word_text = ""
    #
    # except:
    #     word_text = ""

    return "yes"
