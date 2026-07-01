import csv
import re
from datetime import datetime
from .config import DATA_DIR, YORK_TERMS_CSV, REQUESTS_CSV, YORK_FIELDS, REQUEST_FIELDS, BLOCKED_TERMS

SEED_ROWS = [
    {
        "term": "SCAMP",
        "term_type": "acronym",
        "full_form": "Service Catalogue and Management Platform",
        "plain_definition": "A York service management platform used to catalogue services and connect people with service information, support routes, and ownership details.",
        "context": "UIT / Service Management",
        "category": "IT services",
        "status": "verified",
        "source_label": "SCAMP documentation",
        "source_url": "",
        "primary_action_label": "Open SCAMP",
        "primary_action_url": "",
        "related_terms": "Service Catalogue; Halo; KCS",
    },
    {
        "term": "KCS",
        "term_type": "acronym",
        "full_form": "Knowledge-Centred Service",
        "plain_definition": "A method for creating and maintaining support knowledge as part of everyday service work, so answers improve as teams resolve requests.",
        "context": "UIT / Service Desk",
        "category": "IT services",
        "status": "verified",
        "source_label": "KCS overview",
        "source_url": "",
        "primary_action_label": "Submit knowledge article",
        "primary_action_url": "",
        "related_terms": "SCAMP; Knowledge Base; Service Desk",
    },
]

def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())

def normalize_key(value: str) -> str:
    """Return a lookup key that ignores case, punctuation, and spacing."""
    return re.sub(r"[^\w]+", "", normalize_text(value), flags=re.UNICODE).casefold()

def tokenize_lookup_words(value: str) -> list[str]:
    """Split lookup text into searchable words while ignoring punctuation."""
    return re.findall(r"\w+", (value or "").casefold(), flags=re.UNICODE)

def split_related(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]

def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not YORK_TERMS_CSV.exists():
        with YORK_TERMS_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=YORK_FIELDS)
            writer.writeheader()
            writer.writerows(SEED_ROWS)
    if not REQUESTS_CSV.exists():
        with REQUESTS_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUEST_FIELDS + ["created_at"])
            writer.writeheader()

def read_york_terms() -> list[dict]:
    ensure_data_files()
    with YORK_TERMS_CSV.open(newline="", encoding="utf-8") as handle:
        return [{field: row.get(field, "") for field in YORK_FIELDS} for row in csv.DictReader(handle)]

def serialize_entry(row: dict) -> dict:
    item = {field: row.get(field, "") for field in YORK_FIELDS}
    item["related_terms"] = split_related(item.get("related_terms", ""))
    return item

def append_york_definition(fields: dict) -> None:
    ensure_data_files()
    row = {field: normalize_text(fields.get(field, "")) for field in YORK_FIELDS}
    row["term_type"] = row.get("term_type") or "term"
    row["status"] = "community_submitted"
    with YORK_TERMS_CSV.open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=YORK_FIELDS).writerow(row)

def append_definition_request(fields: dict) -> None:
    ensure_data_files()
    row = {field: normalize_text(fields.get(field, "")) for field in REQUEST_FIELDS}
    row["created_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with REQUESTS_CSV.open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=REQUEST_FIELDS + ["created_at"]).writerow(row)

def validate_submission_text(fields: dict) -> tuple[bool, list]:
    errors = []
    combined = " ".join(str(v) for v in fields.values()).casefold()
    for blocked in BLOCKED_TERMS:
        if blocked in combined:
            errors.append(f"Blocked content detected: {blocked}")
    if not normalize_text(fields.get("term", "")):
        errors.append("Term is required.")
    if not normalize_text(fields.get("plain_definition", "")):
        errors.append("Plain definition is required.")
    return not errors, errors
