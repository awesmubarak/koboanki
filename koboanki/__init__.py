from aqt import mw
from aqt.utils import showInfo, qconnect, tr
from aqt.qt import *
import anki.importing as importing
from aqt import forms
from anki.importing.base import Importer
import sqlite3

def akMenuAction() -> None:
    cardCount = mw.col.cardCount()
    forms.importing.Ui_ImportDialog()

    # open file selection menu
    dir_loc = "/Volumes/KOBOeReader"
    file_loc = dir_loc + "/.kobo/KoboReader.sqlite"

    # read in the file list
    connection = sqlite3.connect(file_loc)
    cursor = connection.cursor()
    rows = [row[0] for row in cursor.execute("SELECT text from WordList").fetchall()]

    # add the words to the right file



action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
