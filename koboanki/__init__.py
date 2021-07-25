# Copyright: Awes Mubarak <contact@awesmubarak.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import showInfo, qconnect, tr, getFile
from aqt.qt import *
import sqlite3
import requests
from os import path
from PyQt5.QtWidgets import QFileDialog
import threading
from queue import Queue


def get_link(language_code:str, word:str) -> str:
    return f"https://api.dictionaryapi.dev/api/v2/entries/{language_code}/{word}"


def try_link(link) -> bool:
    "Attempts to connect to a given link. Used to verify internet connection and language codes"
    showInfo(str(link))
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


def queue_handler(queue: Queue, definitions: list) -> Bool:
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
    # TODO: add citation (https://www.lexico.com/about)
    response = []
    try:
        response = requests.get(get_link(language, word)).json()
    except requests.exceptions.ConnectionError:
        definition = ""

    try:
        definition = response[0]["meanings"][0]["definitions"][0]["definition"]
    except:
        definition = ""
    return definition


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

    # get the config file
    config = mw.addonManager.getConfig(__name__)
    if not all(_ for _ in [try_link(l) for l in [get_link(l, "test") for l in config["languageList"]]]):
        showInfo("One or more language codes in the configuration file don't work")
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
