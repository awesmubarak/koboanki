from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *  # type: ignore
from . import utils


class DeckChooserWindow(QDialog):
    def __init__(self):

        QDialog.__init__(self, None)
        self.setGeometry(300, 100, 400, 200)

        # title, confirm button
        self.setWindowTitle("koboanki - choose deck")
        confirm_btn = QPushButton("Confirm")
        confirm_btn.clicked.connect(self.confirm_input)

        # deck list
        self.combo_box = QComboBox(self)
        self.deck_dict = utils.get_deck_dict()
        for (name, _) in self.deck_dict.items():
            self.combo_box.addItem(name)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.combo_box)
        main_layout.addWidget(confirm_btn)
        self.setLayout(main_layout)


    def confirm_input(self):
        self.deck_id = int(self.deck_dict[self.combo_box.currentText()])
        self.close()

    def get_deck_id(self):
        return self.deck_id


class ImportManagerWindow(QDialog):
    def __init__(self, words: dict):
        QDialog.__init__(self, None)
        self.setGeometry(300, 100, 500, 500)
        self.words = words
        self.accept = False # TODO: is there a built in way to do this?

        self.setWindowTitle("koboanki - import words")
        confirm_btn = QPushButton("Add to collection")
        words_tbl = QTableWidget()
        confirm_btn.clicked.connect(self.confirm_input)

        # words table
        n_rows = max(1, len(self.words))
        words_tbl.setColumnCount(2)
        words_tbl.setRowCount(n_rows)
        words_tbl.setHorizontalHeaderLabels(["Word", "Definition"])

        # word definitions
        for w_n, (word, word_def) in enumerate(self.words.items()):
            words_tbl.setItem(w_n, 0, QTableWidgetItem(word))
            words_tbl.setItem(w_n, 1, QTableWidgetItem(word_def))

        main_layout = QVBoxLayout()
        main_layout.addWidget(words_tbl)
        main_layout.addWidget(confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        self.accept = True
        self.close()

    def get_import_status(self):
        return self.accept
