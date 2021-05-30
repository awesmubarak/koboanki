# Copyright: Awes Mubarak <contact@awesmubarak.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import showInfo, qconnect, tr
from aqt.qt import *
import sqlite3
import requests


def getWordList(file_location: str) -> list:
    connection = sqlite3.connect(file_location)
    cursor = connection.cursor()
    rows = [row[0] for row in cursor.execute("SELECT text from WordList").fetchall()]
    return rows


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

    # open file selection menu
    # TODO: open menu for this
    dir_location = "/Volumes/KOBOeReader"
    file_location = dir_location + "/.kobo/KoboReader.sqlite"

    # read in the file list
    wordlist = getWordList(file_location)

    # find repeated words and don't use them because
    ankiWordlist = []
    card = mw.col.sched.getCard()
    while card:
        note = card.note()
        ankiWordlist.append(note.items()[0][1])
        note.flush()
        card = mw.col.sched.getCard()

    newWords = [word for word in wordlist if word not in ankiWordlist]

    # find definitions
    for word in newWords:
        definition = getWordDefinition(word)
        if definition:
            note = mw.col.newNote()
            note["Front"] = word
            note["Back"] = definition
            mw.col.addNote(note)

    # add the words to the right file
    # TODO: this just adds it to a default one i think? idk how this works
    mw.col.save()

    # done
    showInfo("Done importing!")


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
