# -*- coding: utf-8 -*-
#
# Copyright © 2012 Thomas Tempe <thomas.tempe@alysse.org>
# Copyright © 2012 Roland Sieker <ospalh@gmail.com>
# Copyright © 2018 Scott Gigante <scottgigante@gmail.com>
#
# Original: Damien Elmes <anki@ichi2.net> (as japanese/model.py)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

import anki.stdmodels
from anki.lang import _

import genanki
from genanki import Model, Note, Deck

from .augmentation import lookup, tts, silhouette as get_silhouette
from .prestudy import Term
from .css import style
from .card_fields import (
    hanja_button,
    deck_tags,
    korean,
    english,
    sound,
    front_side,
    silhouette,
    comment,
)


# List of fields
######################################################################

fields_list = ["Korean", "English", "Hanja", "Sound", "Silhouette", "Comment"]

# Card templates
######################################################################

recognition_front = u"\n<br>".join([deck_tags, korean])

recall_front = u"\n<br>".join([deck_tags, english, silhouette])

recognition_back = u"\n<br>".join([front_side, english, sound, hanja_button, comment])

recall_back = u"\n<br>".join([front_side, korean, sound, hanja_button, comment])


# Add model for korean word to Anki
######################################################################

model_name = "Korean (jjigae)"

KOREAN_NOTE_MODEL_ID = 2828501749


def get_model() -> Model:
    return Model(
        KOREAN_NOTE_MODEL_ID,
        model_name,
        fields=[
            {"name": "Korean"},
            {"name": "English"},
            {"name": "Hanja"},
            {"name": "Sound"},
            {"name": "Silhouette"},
            {"name": "Comment"},
        ],
        templates=[
            {
                "name": "Recognition",
                "qfmt": recognition_front,
                "afmt": recognition_back,
            },
            {"name": "Recall", "qfmt": recall_front, "afmt": recall_back},
        ],
        css=style,
    )


class KoreanNote(Note):
    def __init__(self, **kwargs):
        super().__init__(get_model(), **kwargs)

    @property
    def guid(self):
        return genanki.guid_for(self.fields[0], self.fields[2])


class ChineseDeck(Deck):
    def __init__(self, deck_id=None, name=None):
        super().__init__(deck_id, name)

    def add_term(self, term: Term, tags=[]):
        the_comment = ""
        the_comment += term.notes
        the_comment += " (amb)" if term.ambiguous else ""

        note = KoreanNote(
            fields=[
                term.word,
                lookup(term.word),
                term.hanja,
                tts(term.word),
                get_silhouette(term.word),
                the_comment,
            ],
            tags=tags,
        )
        self.add_note(note)
        pass


def add_model(col):
    mm = col.models
    m = mm.new(model_name)
    m["id"] = KOREAN_NOTE_MODEL_ID
    # Add fields
    for f in fields_list:
        fm = mm.newField(f)
        mm.addField(m, fm)
    t = mm.newTemplate(u"Recognition")
    t["qfmt"] = recognition_front
    t["afmt"] = recognition_back
    mm.addTemplate(m, t)
    t = mm.newTemplate(u"Recall")
    t["qfmt"] = recall_front
    t["afmt"] = recall_back
    mm.addTemplate(m, t)

    m["css"] += style
    m["addon"] = model_name
    mm.add(m)
    # recognition card
    return m


anki.stdmodels.models.append((lambda: _(model_name), add_model))
