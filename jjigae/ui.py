from aqt import mw

from typing import List, Set, Optional

import genanki

from .prestudy import extract, Term
from .models import Deck

from cached_property import cached_property

# import all of the Qt GUI library
from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QTableWidgetItem,
    QRadioButton,
    pyqtSignal,
    QLineEdit,
    QTableWidget,
    QComboBox,
)
from PyQt5 import QtCore
import logging

RECOMMENDED_TARGET_VOCAB_SIZE = 3500


class LineEditWithFocusedSignal(QLineEdit):
    focused = pyqtSignal()

    def focusInEvent(self, e):
        self.focused.emit()


class PrestudyDialog:
    @classmethod
    def instantiate_and_run(cls):
        cls().show_text_entry_window()

    def show_text_entry_window(self):
        """
        Show the first window of the utility. This window prompts the user to paste in some text.
        """
        self.text_entry_window = w = QWidget(mw, flags=QtCore.Qt.Window)
        w.setWindowTitle(" Prestudy")

        vbox = QVBoxLayout()

        vbox.addWidget(QLabel("Paste in the text you want to read:"))

        self.input_text_box = QTextEdit()
        vbox.addWidget(self.input_text_box)

        continue_button = QPushButton("Continue")
        # TODO not sure why a lambda is needed here
        continue_button.clicked.connect(lambda: self.text_entry_continue_action())
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(continue_button)
        vbox.addLayout(hbox)

        w.setLayout(vbox)

        w.show()

    def text_entry_continue_action(self):
        self.input_text = self.input_text_box.toPlainText()
        self.text_entry_window.close()

        self.show_words_window()

    @cached_property
    def input_words(self) -> Set[str]:
        """
        Return the input after segmenting into words.
        """
        return list(
            extract(self.input_text, min_difficulty="B", max_vocab=self.word_target)
        )

    def show_words_window(self):
        """
        Show the second window of the utility. This window shows the new words that were extracted from the text.
        """
        self.words_window = QWidget(mw, flags=QtCore.Qt.Window)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Enter your vocab size target:"))

        self.vocab_recommended_radio = QRadioButton(
            "{} (Recommended)".format(RECOMMENDED_TARGET_VOCAB_SIZE)
        )
        self.vocab_custom_radio = QRadioButton("Custom: ")
        self.vocab_custom_box = LineEditWithFocusedSignal()

        radio_hbox = QHBoxLayout()
        radio_hbox.addStretch(1)
        radio_hbox.addWidget(self.vocab_recommended_radio)
        radio_hbox.addStretch(2)
        radio_hbox.addWidget(self.vocab_custom_radio)
        radio_hbox.addWidget(self.vocab_custom_box)
        radio_hbox.addStretch(1)
        vbox.addLayout(radio_hbox)

        vbox.addWidget(QLabel("These are the new words you should learn:"))

        self.words_table = self.init_words_table()
        vbox.addWidget(self.words_table)

        continue_hbox = QHBoxLayout()
        continue_hbox.addStretch(1)
        continue_button = QPushButton("Continue")
        continue_hbox.addWidget(continue_button)
        vbox.addLayout(continue_hbox)

        self.words_window.setLayout(vbox)

        self.update_words_table()

        # TODO: for some reason, this disables the blinking cursor in `vocab_custom_box`
        self.vocab_custom_box.focused.connect(lambda: self.vocab_custom_radio.click())
        self.vocab_recommended_radio.clicked.connect(lambda: self.update_words_table())
        self.vocab_custom_radio.clicked.connect(lambda: self.update_words_table())
        self.vocab_custom_box.textChanged.connect(lambda: self.update_words_table())
        continue_button.clicked.connect(lambda: self.words_window_continue_action())

        self.words_window.show()

    def update_words_table(self):
        words_to_study = self.words_to_study
        self.words_table.setRowCount(len(words_to_study))
        for i, term in enumerate(self.words_to_study):
            self.words_table.setItem(i, 0, QTableWidgetItem(term.word))

    @property
    def words_to_study(self) -> List[Term]:
        print(f"UNKNOWN: {self.unknown_words}")
        return sorted(self.unknown_words, key=lambda w: w.rank)

    @property
    def word_target(self):
        if self.vocab_recommended_radio.isChecked():
            return RECOMMENDED_TARGET_VOCAB_SIZE
        if self.vocab_custom_radio.isChecked():
            try:
                return int(self.vocab_custom_box.text())
            except ValueError:
                return 0
        return 0

    @cached_property
    def unknown_words(self) -> List[str]:
        """
        Get words in the text that aren't already studied.
        """
        return [
            word for word in self.input_words if word not in self.words_already_studied
        ]

    @cached_property
    def words_already_studied(self) -> Set[str]:
        def words_for_query(query):
            notes = [mw.col.getNote(id_) for id_ in mw.col.findNotes(query)]
            rv = set()
            for note in notes:
                if "Korean" in note:
                    rv.add(note["Korean"])
            return rv

        suspended = words_for_query("is:suspended")
        not_suspended = words_for_query("-is:suspended")
        not_new = words_for_query("-is:new")

        return not_new | (suspended - not_suspended)

    def init_words_table(self, parent=None):
        """
        Generates a widget that displays a table of words and definitions.
        :param word_def_pairs: list of (word, def) tuples
        :return: a widget
        """
        return QTableWidget(0, 1, parent)

    def words_window_continue_action(self):
        final_touches_window = FinalTouchesWindow(self.words_to_study)

        self.words_window.close()
        final_touches_window.show()


class FinalTouchesWindow(QWidget):
    """
    Window 3/3, allows the user to set deck and tags.
    """

    def __init__(self, vocab_words: List[Term]):
        super().__init__(mw, flags=QtCore.Qt.Window)
        self.vocab_words = vocab_words
        self.init_layout()

    def init_layout(self):
        self.setWindowTitle(" Prestudy")

        vbox = QVBoxLayout()

        vbox.addWidget(QLabel("Select deck to add notes to:"))
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(self.deck_names)
        vbox.addWidget(self.combo_box)

        vbox.addWidget(
            QLabel("(Optional) Enter tag(s) to add to notes, separated by spaces:")
        )
        self.tags_box = QLineEdit()
        vbox.addWidget(self.tags_box)

        hbox = QHBoxLayout()
        self.finish_button = QPushButton("Add Notes")
        hbox.addStretch(1)
        hbox.addWidget(self.finish_button)
        vbox.addLayout(hbox)

        self.finish_button.clicked.connect(lambda: self.add_notes_action())

        self.setLayout(vbox)

    @property
    def deck_names(self):
        return [d["name"] for d in self.decks]

    @property
    def decks(self):
        return sorted(list(mw.col.decks.decks.values()), key=lambda d: d["name"])

    def add_notes_action(self):
        # Checkpoint so user can undo later
        mw.checkpoint("Add Prestudy Notes")

        add_notes(
            self.vocab_words, self.combo_box.currentText(), self.tags_box.text().split()
        )

        # Refresh main window view
        mw.reset()

        self.close()


def add_notes(vocab_words: List[Term], deck_name: str, tags: List[str]):
    # get dict that describes deck
    deck = [d for d in mw.col.decks.decks.values() if d["name"] == deck_name][0]

    # By using the same ID and name as the existing deck, the notes are added to the existing deck, rather than going
    # into a new deck or the default deck.
    out_deck = Deck(deck["id"], deck_name)

    for vocab_word in vocab_words:
        out_deck.add_term(vocab_word, tags=tags)

    # Write the data to the collection
    out_deck.write_to_collection_from_addon()
