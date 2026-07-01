import csv

import nltk
from nltk.corpus import wordnet as wn

from .config import GENERAL_DICTIONARY_CSV
from .data_store import normalize_key, normalize_text

_POS = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}
_DICTIONARY_FIELDS = ["term", "part_of_speech", "definition", "examples", "synonyms"]
_DOWNLOADED = False
_ATTEMPTED_DOWNLOAD = False


def ensure_local_dictionary() -> None:
    GENERAL_DICTIONARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not GENERAL_DICTIONARY_CSV.exists():
        with GENERAL_DICTIONARY_CSV.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=_DICTIONARY_FIELDS).writeheader()


def _split_csv_list(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def _join_csv_list(values: list[str]) -> str:
    return "|".join(normalize_text(value) for value in values if normalize_text(value))


def read_local_dictionary(term: str, max_definitions: int = 3) -> dict:
    normalized_term = normalize_text(term).casefold()
    key = normalize_key(normalized_term)
    if not key:
        return {"term": normalized_term, "definitions": [], "synonyms": []}
    ensure_local_dictionary()
    definitions = []
    synonyms = []
    seen_defs = set()
    with GENERAL_DICTIONARY_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if normalize_key(row.get("term", "")) != key:
                continue
            definition = normalize_text(row.get("definition", ""))
            if definition and definition not in seen_defs and len(definitions) < max_definitions:
                definitions.append({
                    "part_of_speech": normalize_text(row.get("part_of_speech", "")) or "unknown",
                    "definition": definition,
                    "examples": _split_csv_list(row.get("examples", ""))[:2],
                })
                seen_defs.add(definition)
            for synonym in _split_csv_list(row.get("synonyms", "")):
                if synonym.casefold() != normalized_term and synonym not in synonyms:
                    synonyms.append(synonym)
                if len(synonyms) >= 10:
                    break
            if len(definitions) >= max_definitions and len(synonyms) >= 10:
                break
    return {"term": normalized_term, "definitions": definitions, "synonyms": synonyms[:10]}


def save_local_dictionary_entry(entry: dict) -> None:
    term = normalize_text(entry.get("term", "")).casefold()
    if not term:
        return
    ensure_local_dictionary()
    existing_rows = []
    existing_keys = set()
    with GENERAL_DICTIONARY_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            existing_rows.append({field: row.get(field, "") for field in _DICTIONARY_FIELDS})
            existing_keys.add((normalize_key(row.get("term", "")), normalize_text(row.get("definition", ""))))
    synonyms = _join_csv_list(entry.get("synonyms", []))
    new_rows = []
    for definition in entry.get("definitions", []):
        definition_text = normalize_text(definition.get("definition", ""))
        row_key = (normalize_key(term), definition_text)
        if not definition_text or row_key in existing_keys:
            continue
        new_rows.append({
            "term": term,
            "part_of_speech": normalize_text(definition.get("part_of_speech", "")) or "unknown",
            "definition": definition_text,
            "examples": _join_csv_list(definition.get("examples", [])),
            "synonyms": synonyms,
        })
        existing_keys.add(row_key)
    if not new_rows:
        return
    with GENERAL_DICTIONARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_DICTIONARY_FIELDS)
        writer.writeheader()
        writer.writerows(existing_rows + new_rows)


def ensure_wordnet() -> None:
    global _DOWNLOADED, _ATTEMPTED_DOWNLOAD
    if _DOWNLOADED or _ATTEMPTED_DOWNLOAD:
        return
    _ATTEMPTED_DOWNLOAD = True
    wordnet_ready = nltk.download("wordnet", quiet=True)
    omw_ready = nltk.download("omw-1.4", quiet=True)
    _DOWNLOADED = bool(wordnet_ready and omw_ready)


def _lookup_wordnet(term: str, max_definitions: int = 3) -> dict:
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


def lookup_general_dictionary(query: str, max_definitions: int = 3) -> dict:
    term = normalize_text(query).casefold()
    if not term:
        return {"term": term, "definitions": [], "synonyms": []}
    local_entry = read_local_dictionary(term, max_definitions=max_definitions)
    if local_entry["definitions"]:
        return local_entry
    wordnet_entry = _lookup_wordnet(term, max_definitions=max_definitions)
    if wordnet_entry["definitions"]:
        save_local_dictionary_entry(wordnet_entry)
    return wordnet_entry
