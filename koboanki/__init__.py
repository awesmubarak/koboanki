from aqt import mw
from aqt.utils import showInfo, qconnect, tr
from aqt.qt import *
import anki.importing as importing
from aqt import forms
from anki.importing.base import Importer
import sqlite3

import requests

def akMenuAction() -> None:
    cardCount = mw.col.cardCount()
    forms.importing.Ui_ImportDialog()

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
        except:
            pass

    # add the words to the right file

    showInfo("Done importing!")


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
