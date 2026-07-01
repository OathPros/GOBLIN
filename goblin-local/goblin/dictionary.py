import nltk
from nltk.corpus import wordnet as wn

_POS = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}
_DOWNLOADED = False
_ATTEMPTED_DOWNLOAD = False

def ensure_wordnet() -> None:
    global _DOWNLOADED, _ATTEMPTED_DOWNLOAD
    if _DOWNLOADED or _ATTEMPTED_DOWNLOAD:
        return
    _ATTEMPTED_DOWNLOAD = True
    wordnet_ready = nltk.download("wordnet", quiet=True)
    omw_ready = nltk.download("omw-1.4", quiet=True)
    _DOWNLOADED = bool(wordnet_ready and omw_ready)

def lookup_general_dictionary(query: str, max_definitions: int = 3) -> dict:
    term = (query or "").strip().lower()
    if not term:
        return {"term": term, "definitions": [], "synonyms": []}
    ensure_wordnet()
    try:
        synsets = wn.synsets(term.replace(" ", "_"))
    except LookupError:
        return {"term": term, "definitions": [], "synonyms": []}
    definitions = []
    synonyms = []
    seen_defs = set()
    for synset in synsets:
        definition = synset.definition()
        if definition not in seen_defs and len(definitions) < max_definitions:
            definitions.append({
                "part_of_speech": _POS.get(synset.pos(), synset.pos()),
                "definition": definition,
                "examples": synset.examples()[:2],
            })
            seen_defs.add(definition)
        for lemma in synset.lemmas():
            name = lemma.name().replace("_", " ")
            if name.casefold() != term.casefold() and name not in synonyms:
                synonyms.append(name)
            if len(synonyms) >= 10:
                break
        if len(definitions) >= max_definitions and len(synonyms) >= 10:
            break
    return {"term": term, "definitions": definitions, "synonyms": synonyms[:10]}
