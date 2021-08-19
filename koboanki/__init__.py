import requests
import sqlite3
import threading
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo, qconnect
from os import path
from queue import Queue
from PyQt5.QtWidgets import QFileDialog

def get_link(language_code:str, word:str) -> str:
    return f"https://api.dictionaryapi.dev/api/v2/entries/{language_code}/{word}"


def try_link(link) -> bool:
    "Attempts to connect to a given link. Used to verify internet connection and language codes"
    valid = True
    try:
        response = requests.get(link)
        if response.status_code == 404:
            valid = False
    except requests.exceptions.ConnectionError:
        valid = False

    return valid


def get_file_location() -> str:
    """Returns the kobo db file locatoin. Empty if error or not found."""
    folder_name = QFileDialog.getExistingDirectory(
        None, "Select KOBO drive", path.expanduser("~"), QFileDialog.ShowDirsOnly
    )

    if folder_name:
        file_location = path.join(folder_name, ".kobo", "KoboReader.sqlite")
        if not (path.exists(file_location) and path.isfile(file_location)):
            showInfo(f"File path not found: {file_location}")
            file_location = ""
    else:
        file_location = ""

    return file_location


def get_kobo_wordlist(file_location: str) -> list:
    """Opens the kobo file and returns a list of saved words."""
    connection = sqlite3.connect(file_location)
    cursor = connection.cursor()
    wordlist = [
        row[0] for row in cursor.execute("SELECT text from WordList").fetchall()
    ]
    return wordlist


def get_new_wordlist(kobo_wordlist: list) -> list:
    """Returns a list of only words not already added to anki."""
    ids = mw.col.find_notes("")
    anki_wordlist = [mw.col.getNote(id_).items()[0][1] for id_ in ids]
    new_wordlist = [word for word in kobo_wordlist if word not in anki_wordlist]
    return new_wordlist


def get_definitions(wordlist:list, language_list:list) -> tuple:
    """Concurently find defintions for all words"""
    queue = Queue(maxsize=0)
    num_theads = min(50, len(wordlist))
    definitions = [{} for _ in wordlist]
    for i in range(len(wordlist)):
        queue.put((i, wordlist[i], language_list))

    # create threads
    for i in range(num_theads):
        worker = threading.Thread(target=queue_handler, args=(queue,definitions))
        worker.setDaemon(True)
        worker.start()
    queue.join()

    # seperate working and broken words
    definition_dict = {}
    failed_words = []
    for word, definition in zip(wordlist, definitions):
        if definition:
            definition_dict[word] = definition
        else:
            failed_words.append(word)

    return (definition_dict, failed_words)


def queue_handler(queue: Queue, definitions: list) -> bool:
    """"Threads are created pointing at this function to get the word defintions"""
    while not queue.empty():
        work = queue.get()
        word = work[1]
        language_list = work[2]

        definition = ""
        for language in language_list:
            definition = get_word_definition(word, language)
            if definition != "":
                break

        definitions[work[0]] = definition
        queue.task_done()
    return True


def get_word_definition(word: str, language: str) -> str:
    """Return the definition of a word that's passed to it. Empty if no defs."""
    response = []
    word_text = ""
    try:
        response = requests.get(get_link(language, word)).json()
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
    return word_text


def add_to_collection(word_defs: dict) -> None:
    """Adds valid words to the collection"""
    for word, definition in word_defs.items():
        note = mw.col.newNote("Basic")
        note["Front"] = word
        note["Back"] = definition
        mw.col.addNote(note)

    mw.col.save()
    return


def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    # check internet connection
    if not try_link(get_link("en_US", "test")):
        showInfo("Can't access server, faulty internet connection?")
        return

    # get the config file and validate
    config = mw.addonManager.getConfig(__name__)
    if not config:
        showInfo("Config file is empty")
        return
    if not "languageList" in config:
        showInfo("Config file does not contain a language list")
        return
    if len(config["languageList"]) == 0:
        showInfo("Language list is empty")
        return

    links = {code: get_link(code, "test") for code in config["languageList"]}
    links_statuses = {code: try_link(link) for code, link in links.items()}
    failed_codes = [code for code, status in links_statuses.items() if not status]
    if failed_codes:
        showInfo(f"The following language codes are not valid: {failed_codes}")
        return

    # get folder name
    file_location = get_file_location()
    if not file_location:
        return

    # read in the file list
    wordlist = get_kobo_wordlist(file_location)
    if not wordlist:
        showInfo("No saved words found")
        return

    # find newwords, get definitions, add to collection
    new_wordlist = get_new_wordlist(wordlist)
    word_defs, failed_words = get_definitions(new_wordlist, config["languageList"])
    add_to_collection(word_defs)

    # done
    showInfo(
        f"Added words: {[w for w in word_defs.keys()]}\n\nFailed words: {[w for w in failed_words]}"
    )


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
