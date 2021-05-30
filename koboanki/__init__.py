# Copyright: Awes Mubarak <contact@awesmubarak.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import showInfo, qconnect, tr, getFile
from aqt.qt import *
import sqlite3
import requests
from os import path
from PyQt5.QtWidgets import QFileDialog, QWidget


def getWordDefinition(word: str) -> str:
    # TODO: add citation (https://www.lexico.com/about)
    response = requests.get(
        f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}"
    ).json()

    try:
        definition = response[0]["meanings"][0]["definitions"][0]["definition"]
    except:
        definition = ""
    return definition


def akMenuAction() -> None:
    cardCount = mw.col.cardCount()

    # get folder name
    folderName = QFileDialog.getExistingDirectory(
        None, "Select KOBO drive", path.expanduser("~"), QFileDialog.ShowDirsOnly
    )
    if not folderName:
        return 0

    fileLocation = path.join(folderName, ".kobo", "KoboReader.sqlite")
    if not (path.exists(fileLocation) and path.isfile(fileLocation)):
        showInfo(f"File path not found: {fileLocation}")
        return 1

    # read in the file list
    connection = sqlite3.connect(fileLocation)
    cursor = connection.cursor()
    wordlist = [
        row[0] for row in cursor.execute("SELECT text from WordList").fetchall()
    ]

    # find repeated words and don't use them because
    ankiWordList = []

    ids = mw.col.find_notes("")
    ankiWordList = [mw.col.getNote(id_).items()[0][1] for id_ in ids]
    newWords = [word for word in wordlist if word not in ankiWordList]

    # find definitions
    addedWords = []
    failedWords = []
    for word in newWords:
        definition = getWordDefinition(word)
        if definition:
            note = mw.col.newNote()
            note["Front"] = word
            note["Back"] = definition
            mw.col.addNote(note)

            addedWords.append(word)
        else:
            failedWords.append(word)

    # add the words to the right file
    # TODO: this just adds it to a default one i think? idk how this works
    mw.col.save()

    # done
    showInfo("Done importing!")
    showInfo(
        f"Added words: {[w for w in addedWords]}\n\nFailed words: {[w for w in failedWords]}"
    )


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
