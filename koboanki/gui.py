from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
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
        words = utils.get_words(self.config)
        if not words:
            return

        window = ImportManagerWindow(words)
        setattr(mw, "koboannki - import words", window)
        window.exec_()



class ImportManagerWindow(QDialog):
    def __init__(self, words: dict):
        QDialog.__init__(self, None)
        self.setWindowTitle("koboanki - import words")
        self.confirm_btn = QPushButton("Confirm")
        self.words_tbl = QTableWidget()
        self.confirm_btn.clicked.connect(self.confirm_input)

        self.words_tbl.setColumnCount(4)
        self.words_tbl.setRowCount(len(words))
        self.words_tbl.setHorizontalHeaderLabels(["Add", "Word", "Definition", "Blacklist"])

        for w_n, (word, state) in enumerate(words.items()):
            self.words_tbl.setItem(w_n, 1, QTableWidgetItem(word))

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.words_tbl)
        main_layout.addWidget(self.confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        pass


class ChangeCardFormat(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("koboanki - change card format")
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.clicked.connect(self.confirm_input)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        pass
