from pathlib import Path

APP_NAME = "Goblin"
APP_TAGLINE = "Glossary Of Bureaucratic Language and Institutional Nomenclature"
HOST = "127.0.0.1"
PORT = 8765
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
YORK_TERMS_CSV = DATA_DIR / "goblin_york_terms_seed.csv"
REQUESTS_CSV = DATA_DIR / "definition_requests.csv"
GENERAL_DICTIONARY_CSV = DATA_DIR / "general_dictionary.csv"
BLOCKED_TERMS = {"<script", "</script", "javascript:"}
YORK_FIELDS = [
    "term", "term_type", "full_form", "plain_definition", "context", "category",
    "status", "source_label", "source_url", "primary_action_label",
    "primary_action_url", "related_terms",
]
REQUEST_FIELDS = ["term", "suggested_context", "note"]

DESKTOP_CONFIG_PATH = DATA_DIR / "desktop_config.json"
DEFAULT_HOTKEY = "ctrl+shift+y"
