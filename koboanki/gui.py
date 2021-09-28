from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *  # type: ignore
from . import utils


class ImportManagerWindow(QDialog):
    def __init__(self, words: dict):
        QDialog.__init__(self, None)
        self.setGeometry(50, 50, 500, 500)
        self.words = words

        self.setWindowTitle("koboanki - import words")
        confirm_btn = QPushButton("Confirm")
        words_tbl = QTableWidget()
        confirm_btn.clicked.connect(self.confirm_input)

        # words table
        words_tbl.setColumnCount(4)
        words_tbl.setRowCount(len(self.words))
        words_tbl.setHorizontalHeaderLabels(["Add", "Word", "Definition", "Blacklist"])

        for w_n, (word, word_def) in enumerate(self.words.items()):
            add_checkbox = "X" if word_def else " "
            blacklist_checkbox = "X" if not word_def else " "
            words_tbl.setItem(w_n, 0, QTableWidgetItem(add_checkbox))
            words_tbl.setItem(w_n, 1, QTableWidgetItem(word))
            words_tbl.setItem(
                w_n, 2, QTableWidgetItem(word_def)
            )  # TODO: shows HTML not just def :O
            words_tbl.setItem(w_n, 3, QTableWidgetItem(blacklist_checkbox))

        # deck chooser
        self.combo_box = QComboBox(self)

        self.deck_dict = utils.get_deck_dict()
        for (name, _) in self.deck_dict.items():
            self.combo_box.addItem(name)

        main_layout = QVBoxLayout()
        main_layout.addWidget(words_tbl)
        main_layout.addWidget(confirm_btn)
        main_layout.addWidget(self.combo_box)
        self.setLayout(main_layout)

    def confirm_input(self):
        deck_id = self.deck_dict[self.combo_box.currentText()]  # TODO
        utils.add_to_collection(self.words, int(deck_id))
        self.close()
