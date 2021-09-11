from aqt import mw
from aqt.qt import QAction
from aqt.utils import qconnect

from . import utils
from . import gui


def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    config = utils.get_config()  # TODO: use verification thing
    if not config:
        return

    words = utils.get_words(config)
    if not words:
        return

    window = gui.ImportManagerWindow(words)
    setattr(mw, "koboannki - import words", window)
    window.exec_()


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
