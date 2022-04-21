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
    kobo_wordlist = utils.get_kobo_wordlist(utils.get_file_location())

    # filter word list for words not already in deck
    filtered_wordlist = utils.filter_wordlist(kobo_wordlist, deck_id)

    # get definitions
    definitions = {"hi": "greeting"}

    # create cards
    definition_cards = {"hi": "greeting"}

    # display words

    import_window = gui.ImportManagerWindow(definitions)  # type: ignore
    setattr(mw, "koboanki - import manager", deck_window)
    import_window.exec_()
    # deck_id = import_window.get_deck_id()
    import_confirm = import_window.get_import_status()

    # add words to deck

    # utils.add_to_collection(self.words, int(self.deck_id))


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
