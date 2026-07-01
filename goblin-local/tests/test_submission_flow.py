import csv

from goblin import data_store
from goblin.config import YORK_FIELDS, REQUEST_FIELDS
from goblin.server import create_app


def _write_headers(path, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=fields).writeheader()


def test_submitted_definition_is_saved_and_searchable_in_same_session(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    york_terms_csv = data_dir / "goblin_york_terms_seed.csv"
    requests_csv = data_dir / "definition_requests.csv"
    _write_headers(york_terms_csv, YORK_FIELDS)
    _write_headers(requests_csv, REQUEST_FIELDS + ["created_at"])

    monkeypatch.setattr(data_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_store, "YORK_TERMS_CSV", york_terms_csv)
    monkeypatch.setattr(data_store, "REQUESTS_CSV", requests_csv)

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/submit",
        data={
            "term": "EX",
            "full_form": "Example",
            "plain_definition": "A plain-language definition submitted during the test.",
            "source_label": "Example source",
            "source_url": "https://example.test/source",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/entry/EX")

    with york_terms_csv.open(newline="", encoding="utf-8") as handle:
        saved_rows = list(csv.DictReader(handle))
    assert saved_rows == [
        {
            "term": "EX",
            "term_type": "term",
            "full_form": "Example",
            "plain_definition": "A plain-language definition submitted during the test.",
            "context": "",
            "category": "",
            "status": "community_submitted",
            "source_label": "Example source",
            "source_url": "https://example.test/source",
            "primary_action_label": "",
            "primary_action_url": "",
            "related_terms": "",
        }
    ]

    search_response = client.get("/lookup?q=EX")
    search_body = search_response.get_data(as_text=True)
    assert search_response.status_code == 200
    assert "A plain-language definition submitted during the test." in search_body
    assert "Example" in search_body
    assert "Example source" in search_body
