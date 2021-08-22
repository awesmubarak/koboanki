from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QDialog, QPushButton, QVBoxLayout
from . import utils

class PluginWindow(QDialog):
    def __init__(self, config, parent=None):
        QDialog.__init__(self, parent)
        self.config = config

        self.setWindowTitle("koboanki")
        self.import_button = QPushButton("Import words")
        # self.blacklist_button = QPushButton("Change blacklist")
        # self.format_button = QPushButton("Change format")
        self.import_button.clicked.connect(self.import_words)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.import_button)
        self.setLayout(main_layout)

    def import_words(self):
        # TODO: move this into main

        if not utils.verify_config(self.config):
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
        word_defs, failed_words = utils.get_definitions(not_blacklisted, self.config)
        utils.add_to_collection(word_defs)

        # done
        showInfo(
            f"Added words: {[w for w in word_defs.keys()]}\n\nFailed words: {[w for w in failed_words]}"
        )




class ImportManagerWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("koboanki - import words")
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.clicked.connect(self.confirm_input)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        pass
