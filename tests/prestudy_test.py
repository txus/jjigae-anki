from jjigae import prestudy


def test_vocab_is_sorted_by_rank():
    vocabs = prestudy._VOCAB[0:5]
    assert vocabs[0].rank < vocabs[-1].rank


def test_search_finds():
    term = prestudy.search("감정", max_vocab=1000)
    assert term is not None
    assert term.rank == 846
    assert term.word == "감정"
    assert term.hanja == "感情"
    assert term.difficulty == "B"
    assert term.ambiguous


def test_search_does_not_find():
    term = prestudy.search("감정", max_vocab=600)
    assert term is None


def test_extract_words():
    words = prestudy.extract_words(
        "모든 사람은 공동체의 문화생활에 자유롭게 참여하며 예술을 향유하고 과학의 발전과 그 혜택을 공유할 권리를 가진다"
    )
    assert words == {
        "자유롭다",
        "혜택",
        "그",
        "가지다",
        "향유",
        "발전",
        "공유",
        "모든",
        "예술",
        "과학",
        "하다",
        "공동체",
        "문화생활",
        "사람",
        "참여",
        "권리",
    }


def test_extract():
    terms = prestudy.extract(
        "모든 사람은 공동체의 문화생활에 자유롭게 참여하며 예술을 향유하고 과학의 발전과 그 혜택을 공유할 권리를 가진다",
        min_difficulty="B",
    )
    assert {t.word for t in terms} == {"발전", "과학", "자유롭다", "예술", "권리", "참여"}
