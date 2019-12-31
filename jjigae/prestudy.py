import csv
import os
from pathlib import Path
from typing import Optional, Collection, Set
import re

from konlpy.tag import Okt

okt = Okt()
okt.pos("질문이나 건의사항은", norm=True, stem=True)  # warm up

_VOCAB = []

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

path = (ROOT_DIR / "vocab.csv").resolve()

if not path.exists():
    raise Exception(f"Can't find vocab file: {path}")


class Term(object):
    def __init__(self, rank: str, word: str, notes: str, difficulty: str):
        self.rank = None if rank == "" else int(rank)
        self.word = re.sub("[0-9]+", "", word)
        notes = None if notes == "" else notes
        has_hanja = notes and re.search("[\u4e00-\u9fff]", notes)
        self.hanja = notes if has_hanja else None
        self.notes = None if has_hanja else notes
        self.difficulty = difficulty
        self.ambiguous = True if re.search("[0-9]+", word) is not None else False

    def __repr__(self):
        return (
            f"{self.word} ({self.difficulty}, {self.rank}, {self.hanja}, {self.notes})"
        )


def search(word: str, max_vocab: int = 3500) -> Optional[Term]:
    return next((term for term in _VOCAB[:max_vocab] if term.word == word), None)


def extract_words(text: str) -> Set[str]:
    tokens = okt.pos(text, norm=True, stem=True)
    return set(
        [
            word
            for (word, type) in tokens
            if type == "Noun" or type == "Adjective" or type == "Verb"
        ]
    )


def at_least_difficulty(min_difficulty: str, term: Term) -> bool:
    if min_difficulty == "C":
        return term.difficulty == "C"
    elif min_difficulty == "B":
        return term.difficulty == "B" or term.difficulty == "C"
    else:
        return True


def extract(text: str, max_vocab: int = 3500, min_difficulty: str = "A") -> Set[Term]:
    words = extract_words(text)
    return {
        term
        for term in _VOCAB[:max_vocab]
        if term.word in words and at_least_difficulty(min_difficulty, term)
    }


def _load_vocab() -> Collection[Term]:
    with open(path) as file:
        reader = csv.reader(file)
        vocab = []
        for (rank, word, kind, notes, difficulty) in list(reader)[1:]:
            t = Term(rank=rank, word=word, notes=notes, difficulty=difficulty)
            vocab.append(t)
        vocab.sort(key=lambda term: term.rank or 7000)
        return vocab


_VOCAB = _load_vocab()
