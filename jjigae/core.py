# import the main window object (mw) from aqt
from aqt import mw

# import the "show info" tool from utils.py
from aqt.utils import showInfo

# import all of the Qt GUI library
from aqt.qt import QAction

import ndic

from anki.find import Finder

from . import models

from . import hanja

from . import tts

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

import re


def cleanup(txt):
    """Remove all HTML, tags, and others."""
    if not txt:
        return ""
    txt = re.sub(r"<.*?>", "", txt, flags=re.S)
    txt = txt.replace("&nbsp;", " ")
    txt = re.sub(r"^\s*", "", txt)
    txt = re.sub(r"\s*$", "", txt)
    # txt = re.sub(r"[\s+]", " ", txt)
    txt = re.sub(r"\{\{c[0-9]+::(.*?)(::.*?)?\}\}", r"\1", txt)
    return txt


def write_back(note, note_dict, fields):
    for f in fields:
        if f in note_dict and note_dict[f] != note[f]:
            note[f] = note_dict[f]
    note.flush()
    return


def silhouette(hangul):
    def insert_spaces(p):
        r = ""
        for i in p.group(0):
            r += i + " "
        return r[:-1]

    hangul_unicode = "[\u1100-\u11ff|\uAC00-\uD7AF|\u3130-\u318F]"
    hangul = re.sub("{}+".format(hangul_unicode), insert_spaces, hangul)
    txt = re.sub(hangul_unicode, "_", hangul)
    return txt


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
                    translation = ndic.search(korean)
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
                note_dict["Sound"] = tts.get_word_from_google(korean)

            write_back(
                note, note_dict, ["Korean", "English", "Hanja", "Silhouette", "Sound"]
            )

        print(note_dict)

    mw.progress.finish()


def load():
    menu = mw.form.menuTools.addMenu("jjigae")
    action = QAction("Fill missing", mw)
    action.triggered.connect(fill_missing)
    menu.addAction(action)
