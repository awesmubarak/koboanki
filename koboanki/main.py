from aqt import mw
from aqt.qt import QAction, QProgressDialog, QPushButton
from aqt.utils import qconnect

from . import utils
from . import gui


def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    config = utils.get_config()  # TODO: use verification thing
    if not config:
        return

    dlg = QProgressDialog()
    dlg.setAutoClose(True)
    btn = QPushButton("Cancel")
    btn.setEnabled(False)
    dlg.setCancelButton(btn)
    dlg.show()
    dlg.setValue(0)
    words = utils.get_words()
    dlg.setValue(100)
    del dlg

    window = gui.DeckChooserWindow(words)  # type: ignore
    setattr(mw, "koboanki - choose deck to add to", window)
    window.exec_()


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
