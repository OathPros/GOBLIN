# Goblin Local Prototype

**Goblin** is the **Glossary Of Bureaucratic Language and Institutional Nomenclature**. This local Windows proof of concept combines a Flask web/API server with a small Tkinter desktop helper and global hotkeys.

## Setup on Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_goblin.py
```

The app starts a local server at <http://127.0.0.1:8765> and a small "Goblin is running" control window. Highlight text anywhere and press the configured shortcut (default: `Ctrl+Shift+Y`) to open a popup. Use **Set shortcut** in the control window to choose a custom hotkey.

## What it does

- Shows York-specific CSV definitions first, matching case-insensitively while ignoring punctuation and spacing.
- Falls back to definitions and synonyms saved in `data/general_dictionary.csv`, then uses NLTK WordNet for missing terms and saves successful WordNet lookups back to that local CSV. If selected text contains multiple unrecognized words, Goblin shows up to two definitions for each word.
- Lets anyone submit a York definition with no authentication for this prototype.
- Appends submitted definitions immediately to `data/goblin_york_terms_seed.csv`.
- Saves definition requests to `data/definition_requests.csv`.

## Local dictionary CSV

Goblin stores general dictionary rows in `data/general_dictionary.csv` with the columns `term`, `part_of_speech`, `definition`, `examples`, and `synonyms`. Separate multiple examples or synonyms with `|`. You can edit this CSV directly, and successful WordNet lookups are cached there automatically for future offline use.

## Useful URLs

- Search: <http://127.0.0.1:8765/>
- API lookup: <http://127.0.0.1:8765/api/lookup?q=SCAMP>
- Submit: <http://127.0.0.1:8765/submit?term=SCAMP>
- Request: <http://127.0.0.1:8765/request-definition?term=SCAMP>

## Troubleshooting

- If the global shortcut does not work, run the terminal as a normal user first; avoid administrator mode unless needed.
- If selected text capture fails, copy text manually and press the shortcut.
- If WordNet download fails, run Python and execute `import nltk; nltk.download("wordnet"); nltk.download("omw-1.4")`.
- Some apps may block simulated `Ctrl+C`; use manual copy fallback.
- If the default `Ctrl+Shift+Y` shortcut conflicts with another app, click **Set shortcut** and enter another `keyboard` hotkey string such as `ctrl+alt+g`.
