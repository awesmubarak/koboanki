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
        self.words = words

        self.setWindowTitle("koboanki - import words")
        self.confirm_btn = QPushButton("Confirm")
        self.words_tbl = QTableWidget()
        self.confirm_btn.clicked.connect(self.confirm_input)

        self.words_tbl.setColumnCount(4)
        self.words_tbl.setRowCount(len(self.words))
        self.words_tbl.setHorizontalHeaderLabels(
            ["Add", "Word", "Definition", "Blacklist"]
        )

        for w_n, (word, word_def) in enumerate(self.words.items()):
            add_checkbox = "X" if word_def else " "
            blacklist_checkbox = "X" if not word_def else " "
            self.words_tbl.setItem(w_n, 0, QTableWidgetItem(add_checkbox))
            self.words_tbl.setItem(w_n, 1, QTableWidgetItem(word))
            self.words_tbl.setItem(w_n, 2, QTableWidgetItem(word_def))
            self.words_tbl.setItem(w_n, 3, QTableWidgetItem(blacklist_checkbox))

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.words_tbl)
        main_layout.addWidget(self.confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        utils.add_to_collection(self.words)


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
