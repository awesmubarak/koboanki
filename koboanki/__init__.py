# Copyright: Awes Mubarak <contact@awesmubarak.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import showInfo, qconnect, tr, getFile
from aqt.qt import *
import sqlite3
import requests
from os import path
from PyQt5.QtWidgets import QFileDialog
from sys import exit


def getWordDefinition(word: str) -> str:
    """Return the definition of a word that's passed to it. Empty if no definition"""
    # TODO: add citation (https://www.lexico.com/about)
    response = requests.get(
        f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}"
    ).json()

    try:
        definition = response[0]["meanings"][0]["definitions"][0]["definition"]
    except:
        definition = ""
    return definition


def getFileName() -> str:
    """Returns a file location for the sqlite3 database. Empty if error or not found."""
    folderName = QFileDialog.getExistingDirectory(
        None, "Select KOBO drive", path.expanduser("~"), QFileDialog.ShowDirsOnly
    )

    if folderName:
        fileLocation = path.join(folderName, ".kobo", "KoboReader.sqlite")
        if not (path.exists(fileLocation) and path.isfile(fileLocation)):
            showInfo(f"File path not found: {fileLocation}")
            fileLocation = ""
    else:
        fileLocation = ""

    return fileLocation


def getKoboWordList(fileLocation: str) -> list:
    """Opens the kobo file and returns a list of saved words."""
    connection = sqlite3.connect(fileLocation)
    cursor = connection.cursor()
    wordlist = [
        row[0] for row in cursor.execute("SELECT text from WordList").fetchall()
    ]
    return wordlist


def getNeworldList(koboWordList: list) -> list:
    """Returns a list of only words not already added to anki."""
    ids = mw.col.find_notes("")
    ankiWordList = [mw.col.getNote(id_).items()[0][1] for id_ in ids]
    newWords = [word for word in koboWordList if word not in ankiWordList]
    return newWords


def getDefinitions(wordList: list) -> tuple:
    """Finds the definition for each word. If not definition is found adds to a list."""
    wordDict = {}
    failedWods = []
    for word in wordList:
        definition = getWordDefinition(word)
        if definition:
            wordDict[word] = definition
        else:
            failedWods.append(word)
    return (wordDict, failedWods)


def addToCol(wordDict: dict) -> None:
    """Adds valid words to the collection"""
    for word, definition in wordDict.items():
        note = mw.col.newNote()
        note["Front"] = word
        note["Back"] = definition
        mw.col.addNote(note)

    mw.col.save()
    return


def akMenuAction() -> None:
    """Main function, binds to menu item"""
    # get folder name
    fileLocation = getFileName()

    if not fileLocation:
        return

    # read in the file list
    wordlist = getKoboWordList(fileLocation)

    if not wordlist:
        showInfo("No saved words found")
        return

    # find newwords, get definitions, add to collection
    newWords = getNeworldList(wordlist)
    wordDict, failedWords = getDefinitions(newWords)
    addToCol(wordDict)

    # done
    showInfo(
        f"Added words: {[w for w in wordDict.keys()]}\n\nFailed words: {[w for w in failedWords]}"
    )


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
