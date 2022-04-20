from aqt import mw
from aqt.qt import QAction, QProgressDialog, QPushButton
from aqt.utils import qconnect, showInfo

from . import utils
from . import gui


def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    config = utils.get_config()  # TODO: use verification thing
    if not config:
        return

    # chose deck to add words to
    deck_window = gui.DeckChooserWindow()  # type: ignore
    setattr(mw, "koboanki - choose deck to add to", deck_window)
    deck_window.exec_()
    deck_id = deck_window.get_deck_id()

    # get word list from kobo
    kobo_words_list = utils.get_words()

    # filter word list for words not already in deck

    # get definitions

    # display words


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
