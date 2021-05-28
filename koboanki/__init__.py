from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *

def akMenuAction() -> None:
    cardCount = mw.col.cardCount()
    showInfo("Card count: %d" % cardCount)

    # open file selection menu


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, akMenuAction)
mw.form.menuTools.addAction(action)
