from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo, qconnect

from . import utils
from . import gui

def koboanki_menu_action() -> None:
    """Main function, binds to menu item"""

    window = gui.PluginWindow()
    setattr(mw, "koboannki", window)
    window.exec_()

    # get the config file and validate
    config = utils.get_config()
    if not config:
        return

    if not utils.verify_config(config):
        return

    blacklist = utils.get_blacklist()
    if not blacklist:
        showInfo("No valid blacklist found")
        return

    # get folder name
    file_location = utils.get_file_location()
    if not file_location:
        return

    # read in the word list
    wordlist = utils.get_kobo_wordlist(file_location)
    if not wordlist:
        showInfo("No saved words found")
        return

    # check internet connection
    if not utils.try_link(utils.get_link("en_US", "test")):
        showInfo("Can't access server, faulty internet connection?")
        return

    # find newwords, get definitions, add to collection
    new_wordlist = utils.get_new_wordlist(wordlist)
    not_blacklisted = [word for word in new_wordlist if word not in blacklist]
    word_defs, failed_words = utils.get_definitions(not_blacklisted, config)
    utils.add_to_collection(word_defs)

    # done
    showInfo(
        f"Added words: {[w for w in word_defs.keys()]}\n\nFailed words: {[w for w in failed_words]}"
    )


action = QAction("Import KOBO wordlist", mw)
qconnect(action.triggered, koboanki_menu_action)
mw.form.menuTools.addAction(action)
