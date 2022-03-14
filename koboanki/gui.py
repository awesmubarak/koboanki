from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *  # type: ignore
from . import utils


class DeckChooserWindow(QDialog):
    def __init__(self, words):

        QDialog.__init__(self, None)
        self.setGeometry(50, 50, 500, 500)
        self.words = words

        self.setWindowTitle("koboanki - import words")
        confirm_btn = QPushButton("Confirm")
        confirm_btn.clicked.connect(self.confirm_input)

        self.combo_box = QComboBox(self)

        self.deck_dict = utils.get_deck_dict()
        for (name, _) in self.deck_dict.items():
            self.combo_box.addItem(name)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.combo_box)
        main_layout.addWidget(confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        deck_id = self.deck_dict[self.combo_box.currentText()]  # TODO
        words = utils.get_words()
        window = ImportManagerWindow(self.words, deck_id)  # type: ignore
        setattr(mw, "koboannki - import words", window)
        self.hide()
        window.exec_()
        self.close()


class ImportManagerWindow(QDialog):
    def __init__(self, words: dict, deck_id):
        QDialog.__init__(self, None)
        self.setGeometry(50, 50, 500, 500)
        self.words = words

        self.setWindowTitle("koboanki - import words")
        confirm_btn = QPushButton("Confirm")
        words_tbl = QTableWidget()
        confirm_btn.clicked.connect(self.confirm_input)

        # words table
        n_rows = max(1, len(self.words))
        words_tbl.setColumnCount(5)
        words_tbl.setRowCount(n_rows)
        words_tbl.setHorizontalHeaderLabels(["A", "I", "B", "Word", "Definition"])

        # word definitions
        for w_n, (word, word_def) in enumerate(self.words.items()):
            words_tbl.setItem(w_n, 3, QTableWidgetItem(word))
            words_tbl.setItem(w_n, 4, QTableWidgetItem(word_def))

        # add or don't add checkboxes
        for y in range(3):
            button_group = QButtonGroup(self)
            button_group.setExclusive(True)
            for x in range(n_rows):
                checkbox = QRadioButton()
                button_group.addButton(checkbox)
                words_tbl.setCellWidget(y, x, checkbox)

        main_layout = QVBoxLayout()
        main_layout.addWidget(words_tbl)
        main_layout.addWidget(confirm_btn)
        self.setLayout(main_layout)

    def confirm_input(self):
        deck_id = self.deck_dict[self.combo_box.currentText()]  # TODO
        utils.add_to_collection(self.words, int(deck_id))
        self.close()
