"""
app.py – Flask-Server für das KI-Assistenzsystem

Stellt zwei Endpunkte bereit:
- POST /api/generate  → Dokument erstellen
- GET  /api/example   → Beispieldaten laden

Das Frontend wird als statische Dateien aus dem frontend/-Ordner ausgeliefert.
"""

import logging
import os
from datetime import datetime, date

# Lokale .env-Datei laden (für GROQ_API_KEY etc.) – optional.
# Auf Render kommen die Variablen direkt aus der Umgebung.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv ist optional

from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

from document_logic import create_document, get_example_data
from pdf_export import create_pdf
from docx_export import create_docx
from speech_to_text import transcribe_audio, extract_fields
from template_manager import save_template, list_templates, load_template, delete_template, rename_template

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _safe_download_filename(label: str, datum_iso: str, ext: str) -> str:
    """Erzeugt einen Header-sicheren Dateinamen für Content-Disposition.
    Verhindert CRLF-Injection / Header-Smuggling über die Metadaten."""
    base = secure_filename(f"{label}_{datum_iso}") or "Dokument"
    return f"{base}.{ext}"

_DOC_LABELS = {
    "aktenvermerk":          "Aktenvermerk",
    "telefonnotiz":          "Telefonnotiz",
    "besprechungsprotokoll": "Besprechungsprotokoll",
}


def _datum_to_iso(datum: str) -> str:
    try:
        return datetime.strptime(datum, "%d.%m.%Y").strftime("%Y-%m-%d")
    except Exception:
        return date.today().strftime("%Y-%m-%d")

# Flask-App konfigurieren
# Das Frontend liegt einen Ordner höher unter /frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.json.ensure_ascii = False

# Maximale Größe einer Anfrage – schützt vor unbeabsichtigtem oder
# böswilligem Hochladen sehr großer Audio- oder JSON-Daten (DoS).
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB


@app.after_request
def _add_security_headers(response):
    """Setzt grundlegende Security-Header auf jede Antwort."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "microphone=(self), camera=()")
    # Content-Security-Policy bewusst zurückhaltend, weil wir Inline-Handler
    # in dieser Prototyp-Version noch nutzen. Für Produktion siehe TODO.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "img-src 'self' data:; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )
    return response


@app.errorhandler(413)
def _too_large(_e):
    return jsonify({
        "success": False,
        "errors": ["Die Anfrage ist zu groß (max. 25 MB). Bitte kürzere Audioaufnahme oder kleinere Eingabe verwenden."]
    }), 413


# ============================================================================
# FRONTEND AUSLIEFERN
# ============================================================================

@app.route("/")
def index():
    """Startseite ausliefern."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """CSS, JS und andere statische Dateien ausliefern."""
    return send_from_directory(FRONTEND_DIR, filename)


# ============================================================================
# API-ENDPUNKTE
# ============================================================================

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Dokument generieren.

    Erwartet JSON:
    {
        "doc_type": "aktenvermerk" | "telefonnotiz" | "besprechungsprotokoll",
        "datum": "...",
        "uhrzeit": "...",
        "beteiligte": "...",
        "betreff": "...",
        "notizen": "...",
        "naechste_schritte": "..."
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "errors": ["Keine Daten empfangen. Bitte das Formular ausfüllen."]
        }), 400

    doc_type = data.get("doc_type", "")

    # Pro-Feld-Längenlimits: Schutz gegen Missbrauch (zu großer LLM-Prompt,
    # OOM, Token-Kosten). Werte sind großzügig gewählt, decken aber realistische
    # Verwaltungseinträge ab.
    FIELD_LIMITS = {
        "datum": 20, "uhrzeit": 20,
        "beteiligte": 500, "betreff": 500,
        "notizen": 5000, "naechste_schritte": 5000,
    }

    def _truncate(value, limit):
        s = (value or "").strip() if isinstance(value, str) else ""
        return s[:limit]

    # Eingabedaten für die Dokumentlogik zusammenstellen
    doc_data = {k: _truncate(data.get(k, ""), FIELD_LIMITS[k]) for k in FIELD_LIMITS}

    # Dokument erstellen (inkl. Validierung)
    result = create_document(doc_type, doc_data)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 422


@app.route("/api/export-pdf", methods=["POST"])
def api_export_pdf():
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify({"success": False, "errors": ["Kein Text vorhanden."]}), 400

    text     = data["text"]
    doc_type = data.get("doc_type", "")
    metadata = data.get("metadata", {})

    pdf_bytes = create_pdf(text, doc_type, metadata)
    label    = _DOC_LABELS.get(doc_type, "Dokument")
    filename = _safe_download_filename(label, _datum_to_iso(metadata.get("datum", "")), "pdf")

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/export-docx", methods=["POST"])
def api_export_docx():
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify({"success": False, "errors": ["Kein Text vorhanden."]}), 400

    text     = data["text"]
    doc_type = data.get("doc_type", "")
    metadata = data.get("metadata", {})

    docx_bytes = create_docx(text, doc_type, metadata)
    label      = _DOC_LABELS.get(doc_type, "Dokument")
    filename   = _safe_download_filename(label, _datum_to_iso(metadata.get("datum", "")), "docx")
    mime       = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return Response(
        docx_bytes,
        mimetype=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    """
    Schritt 1: Spracherkennung – Audio zu Text (Whisper).

    Erwartet: Audio-Datei als multipart/form-data (Feld: "audio")
    Gibt zurück: {"success": true, "text": "..."}
    """
    if "audio" not in request.files:
        return jsonify({"success": False, "errors": ["Keine Audiodatei empfangen."]}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()

    if len(audio_bytes) == 0:
        return jsonify({"success": False, "errors": ["Leere Audiodatei."]}), 400

    try:
        text = transcribe_audio(audio_bytes, audio_file.filename or "audio.webm")
        if not text:
            return jsonify({"success": False, "errors": ["Keine Sprache erkannt. Bitte erneut versuchen."]}), 200
        return jsonify({"success": True, "text": text}), 200
    except ImportError:
        logger.exception("faster-whisper ist nicht installiert")
        return jsonify({
            "success": False,
            "errors": ["Lokale Spracherkennung nicht verfügbar. In der Cloud-Demo bitte die Browser-Spracheingabe nutzen."]
        }), 503
    except Exception:
        logger.exception("Fehler bei der Spracherkennung")
        return jsonify({"success": False, "errors": ["Fehler bei der Spracherkennung. Bitte erneut versuchen."]}), 500


@app.route("/api/extract-fields", methods=["POST"])
def api_extract_fields():
    """
    Schritt 2: Strukturierte Felder aus Text extrahieren (Ollama).

    Erwartet JSON: {"text": "...", "doc_type": "..."}
    Gibt zurück: {"success": true, "fields": {...}}
    """
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify({"success": False, "errors": ["Kein Text vorhanden."]}), 400

    try:
        fields = extract_fields(data["text"], data.get("doc_type", "aktenvermerk"))
        return jsonify({"success": True, "fields": fields}), 200
    except Exception:
        logger.exception("Fehler bei der Feldextraktion")
        return jsonify({"success": False, "errors": ["Fehler bei der Feldextraktion."]}), 500


@app.route("/api/templates", methods=["GET"])
def api_templates_list():
    """Alle gespeicherten Vorlagen auflisten."""
    return jsonify(list_templates()), 200


@app.route("/api/templates", methods=["POST"])
def api_templates_save():
    """Vorlage speichern."""
    data = request.get_json()
    if not data or not data.get("name", "").strip():
        return jsonify({"success": False, "errors": ["Bitte einen Namen eingeben."]}), 400

    result = save_template(
        name=data["name"].strip(),
        doc_type=data.get("doc_type", ""),
        fields=data.get("fields", {})
    )
    return jsonify(result), 200


@app.route("/api/templates/<filename>", methods=["GET"])
def api_templates_load(filename):
    """Eine Vorlage laden."""
    template = load_template(filename)
    if not template:
        return jsonify({"success": False, "errors": ["Vorlage nicht gefunden."]}), 404
    return jsonify(template), 200


@app.route("/api/templates/<filename>/rename", methods=["POST"])
def api_templates_rename(filename):
    """Eine Vorlage umbenennen."""
    data = request.get_json()
    new_name = data.get("new_name", "").strip() if data else ""
    if not new_name:
        return jsonify({"success": False, "errors": ["Bitte einen neuen Namen eingeben."]}), 400
    result = rename_template(filename, new_name)
    if not result:
        return jsonify({"success": False, "errors": ["Vorlage nicht gefunden."]}), 404
    return jsonify(result), 200


@app.route("/api/templates/<filename>", methods=["DELETE"])
def api_templates_delete(filename):
    """Eine Vorlage loeschen."""
    if delete_template(filename):
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "errors": ["Vorlage nicht gefunden."]}), 404


@app.route("/api/example", methods=["GET"])
def api_example():
    """Beispieldaten für einen Dokumenttyp laden."""
    doc_type = request.args.get("doc_type", "aktenvermerk")
    example = get_example_data(doc_type)
    return jsonify(example), 200


# ============================================================================
# SERVER STARTEN
# ============================================================================

if __name__ == "__main__":
    import socket
    # Lokale IP-Adresse ermitteln für Netzwerkzugriff
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("\n" + "=" * 55)
    print("  KI-Assistenzsystem für Verwaltungsdokumente")
    print("  Prototyp – Projektstudie")
    print("=" * 55)
    print(f"\n  Lokal:     http://localhost:5000")
    print(f"  Netzwerk:  http://{local_ip}:5000")
    print(f"  Beenden mit: Strg + C\n")

    # host="0.0.0.0" → erlaubt Zugriff von anderen Geräten im Netzwerk
    # Debug-Modus ist standardmäßig AUS und nur über die Umgebungsvariable
    # FLASK_DEBUG=1 aktivierbar (Werkzeug-Debugger ist eine RCE-Schwachstelle,
    # wenn er ungewollt erreichbar ist).
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
