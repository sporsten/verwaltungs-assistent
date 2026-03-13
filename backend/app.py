"""
app.py – Flask-Server für das KI-Assistenzsystem

Stellt zwei Endpunkte bereit:
- POST /api/generate  → Dokument erstellen
- GET  /api/example   → Beispieldaten laden

Das Frontend wird als statische Dateien aus dem frontend/-Ordner ausgeliefert.
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from document_logic import create_document, get_example_data

# Flask-App konfigurieren
# Das Frontend liegt einen Ordner höher unter /frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


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

    # Eingabedaten für die Dokumentlogik zusammenstellen
    doc_data = {
        "datum": data.get("datum", ""),
        "uhrzeit": data.get("uhrzeit", ""),
        "beteiligte": data.get("beteiligte", ""),
        "betreff": data.get("betreff", ""),
        "notizen": data.get("notizen", ""),
        "naechste_schritte": data.get("naechste_schritte", "")
    }

    # Dokument erstellen (inkl. Validierung)
    result = create_document(doc_type, doc_data)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 422


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
    app.run(debug=True, host="0.0.0.0", port=5000)
