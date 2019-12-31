import re
import ndic
from .tts import get_word_from_google


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


def tts(korean) -> str:
    return get_word_from_google(korean)


def lookup(korean) -> str:
    return ndic.search(korean)
