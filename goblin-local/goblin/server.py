from urllib.parse import quote
from flask import Flask, jsonify, redirect, render_template, request, url_for
from .config import APP_NAME, APP_TAGLINE, HOST, PORT
from .data_store import append_definition_request, append_york_definition, ensure_data_files, validate_submission_text
from .lookup import lookup

# Future production hook: add SSO/session authentication and authorization checks before writes.
def create_app() -> Flask:
    ensure_data_files()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.update(APP_NAME=APP_NAME, APP_TAGLINE=APP_TAGLINE)

    @app.get("/")
    def index():
        q = request.args.get("q", "")
        result = lookup(q) if q else None
        return render_template("index.html", q=q, result=result)

    @app.get("/lookup")
    def lookup_page():
        q = request.args.get("q", "")
        return render_template("index.html", q=q, result=lookup(q) if q else None)

    @app.get("/api/lookup")
    def api_lookup():
        return jsonify(lookup(request.args.get("q", "")))

    @app.route("/submit", methods=["GET", "POST"])
    def submit():
        errors = []
        values = {k: request.values.get(k, "") for k in ["term", "full_form", "plain_definition", "context", "category", "source_label", "source_url", "primary_action_label", "primary_action_url", "related_terms"]}
        if request.method == "POST":
            valid, errors = validate_submission_text(values)
            if valid:
                append_york_definition(values)
                return redirect(url_for("entry", term=values["term"]))
        return render_template("submit.html", values=values, errors=errors)

    @app.route("/request-definition", methods=["GET", "POST"])
    def request_definition():
        values = {k: request.values.get(k, "") for k in ["term", "suggested_context", "note"]}
        saved = False
        if request.method == "POST":
            append_definition_request(values)
            saved = True
        return render_template("request_definition.html", values=values, saved=saved)

    @app.get("/entry/<path:term>")
    def entry(term):
        return render_template("entry.html", term=term, result=lookup(term), quote=quote)

    return app

def run_server() -> None:
    create_app().run(host=HOST, port=PORT, debug=False, use_reloader=False)
