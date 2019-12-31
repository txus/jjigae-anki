# import the main window object (mw) from aqt
from aqt import mw

# import the "show info" tool from utils.py
from aqt.utils import showInfo, askUserDialog

# import all of the Qt GUI library
from aqt.qt import QAction

import ndic

from anki.find import Finder

from typing import Set

from . import models

from . import hanja

from .ui import PrestudyDialog
from .augmentation import cleanup, silhouette, tts, lookup

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

import re


def write_back(note, note_dict, fields):
    for f in fields:
        if f in note_dict and note_dict[f] != note[f]:
            note[f] = note_dict[f]
    note.flush()
    return


def fill_missing():
    notes = Finder(mw.col).findNotes("deck:current")
    mw.progress.start(immediate=True, min=0, max=len(notes))
    scanned = 0
    for noteId in notes:
        scanned += 1
        note = mw.col.getNote(noteId)
        note_dict = dict(note)

        if "Korean" in note_dict:
            korean = cleanup(note_dict["Korean"])

            if "English" in note_dict and cleanup(note_dict["English"]) == "":
                mw.progress.update(label=f"[{korean}] Translating...", value=scanned)
                english = cleanup(note_dict["English"])
                if korean != "" and english == "":
                    translation = lookup(korean)
                    note_dict["Korean"] = korean
                    note_dict["English"] = translation

            if "Hanja" in note_dict and cleanup(note_dict["Hanja"]) == "":
                mw.progress.update(
                    label=f"[{korean}] Looking up Hanja...", value=scanned
                )
                found = hanja.lookup(korean)
                if found is not None:
                    note_dict["Hanja"] = found["hanja"]

            if "Silhouette" in note_dict and cleanup(note_dict["Silhouette"]) == "":
                mw.progress.update(
                    label=f"[{korean}] Processing silhouette...", value=scanned
                )
                note_dict["Silhouette"] = silhouette(korean)

            if "Sound" in note_dict and cleanup(note_dict["Sound"]) == "":
                mw.progress.update(
                    label=f"[{korean}] Looking up sound...", value=scanned
                )
                note_dict["Sound"] = tts(korean)

            write_back(
                note, note_dict, ["Korean", "English", "Hanja", "Silhouette", "Sound"]
            )

        print(note_dict)

    mw.progress.finish()


def load():
    menu = mw.form.menuTools.addMenu("jjigae")
    action = QAction("Fill missing", mw)
    action.triggered.connect(fill_missing)
    xaction = QAction("Prestudy", mw)
    xaction.triggered.connect(PrestudyDialog.instantiate_and_run)
    menu.addAction(action)
    menu.addAction(xaction)
