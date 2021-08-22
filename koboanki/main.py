from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo, qconnect

from . import utils
from . import gui

def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    config = utils.get_config()
    if not config:
        return

    window = gui.PluginWindow(config)
    setattr(mw, "koboannki", window)
    window.exec_()

action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
