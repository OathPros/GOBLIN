# Goblin Local Prototype

**Goblin** is the **Glossary Of Bureaucratic Language and Institutional Nomenclature**. This local Windows proof of concept combines a Flask web/API server with a small Tkinter desktop helper and global hotkeys.

## Setup on Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_goblin.py
```

The app starts a local server at <http://127.0.0.1:8765> and a small "Goblin is running" control window. Highlight text anywhere and press `Ctrl+Shift+Y` or `Ctrl+Alt+Y` to open a popup.

## What it does

- Shows York-specific CSV definitions first.
- Falls back to NLTK WordNet dictionary definitions and synonyms.
- Lets anyone submit a York definition with no authentication for this prototype.
- Appends submitted definitions immediately to `data/goblin_york_terms_seed.csv`.
- Saves definition requests to `data/definition_requests.csv`.

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
- `Ctrl+Shift+Y` may conflict with some apps; use `Ctrl+Alt+Y` fallback.
