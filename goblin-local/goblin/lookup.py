from difflib import get_close_matches
from .data_store import normalize_key, normalize_text, read_york_terms, serialize_entry, split_related, tokenize_lookup_words
from .dictionary import lookup_general_dictionary

def _matches_related(row: dict, key: str) -> bool:
    return any(normalize_key(alias) == key for alias in split_related(row.get("related_terms", "")))

def lookup(query: str) -> dict:
    display_query = normalize_text(query or "")
    key = normalize_key(display_query)
    rows = read_york_terms()
    york = []
    if key:
        for predicate in (
            lambda row: normalize_key(row.get("term")) == key,
            lambda row: normalize_key(row.get("full_form")) == key,
            lambda row: _matches_related(row, key),
        ):
            for row in rows:
                if predicate(row) and row not in york:
                    york.append(row)
            if york:
                break
        if not york:
            choices = {normalize_key(row.get("term")): row for row in rows if row.get("term")}
            choices.update({normalize_key(row.get("full_form")): row for row in rows if row.get("full_form")})
            for match in get_close_matches(key, choices.keys(), n=3, cutoff=0.78):
                if choices[match] not in york:
                    york.append(choices[match])
    word_definitions = []
    words = tokenize_lookup_words(display_query)
    if len(words) > 1 and not york:
        seen_words = []
        for word in words:
            if word not in seen_words:
                seen_words.append(word)
                word_definitions.append(lookup_general_dictionary(word, max_definitions=2))
    return {
        "query": display_query,
        "normalized_query": key,
        "york_results": [serialize_entry(row) for row in york],
        "general_dictionary": lookup_general_dictionary(display_query),
        "word_definitions": word_definitions,
    }
