from aqt import mw
from aqt.utils import showInfo, qconnect, tr
from aqt.qt import *
import sqlite3

import requests

def akMenuAction() -> None:
    cardCount = mw.col.cardCount()

    # open file selection menu
    # TODO: open menu for this
    dir_loc = "/Volumes/KOBOeReader"
    file_loc = dir_loc + "/.kobo/KoboReader.sqlite"

    # read in the file list
    connection = sqlite3.connect(file_loc)
    cursor = connection.cursor()
    rows = [row[0] for row in cursor.execute("SELECT text from WordList").fetchall()]

    # find definitions
    # TODO: use an acctual module for this lmao
    for word in rows:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}").json()
        try:
            definition = response[0]["meanings"][0]["definitions"][0]["definition"]
            note = mw.col.newNote()
            note["Front"] = word
            note["Back"] = definition
            mw.col.addNote(note)
        except:
            pass

    # add the words to the right file
    mw.col.save()

    # done
    showInfo("Done importing!")


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
