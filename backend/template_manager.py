"""
template_manager.py – Vorlagen speichern, laden und löschen.

Vorlagen werden als JSON-Dateien im Ordner backend/vorlagen/ gespeichert.
Jede Vorlage enthält den Dokumenttyp und die Formulardaten.

Sicherheit: Alle Dateipfade werden gegen Pfad-Traversal geprüft
(_safe_filepath). Es ist unmöglich, Dateien außerhalb von VORLAGEN_DIR
zu lesen, zu schreiben oder zu löschen.
"""

import json
import logging
import os
import re
import unicodedata

logger = logging.getLogger(__name__)

VORLAGEN_DIR = os.path.realpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "vorlagen")
)

# Ordner erstellen falls nicht vorhanden
os.makedirs(VORLAGEN_DIR, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    """Vorlagenname in sicheren Dateinamen umwandeln."""
    # Unicode normalisieren (Umlaute etc.)
    name = unicodedata.normalize("NFKD", name)
    # Nur Buchstaben, Zahlen, Leerzeichen, Bindestriche behalten
    name = re.sub(r"[^\w\s\-]", "", name, flags=re.UNICODE)
    name = name.strip().replace(" ", "_")
    if not name:
        name = "vorlage"
    return name[:80]


def _safe_filepath(filename: str):
    """Verhindert Pfad-Traversal: gibt einen absoluten Pfad zurück, der
    GARANTIERT innerhalb von VORLAGEN_DIR liegt – sonst None.

    Damit sind Angriffe wie '../../app.py', URL-encoded Slash-Sequenzen
    oder absolute Pfade ('/etc/passwd') wirkungslos."""
    if not filename or not isinstance(filename, str):
        return None
    # Verzeichnis-Komponenten verbieten
    if "/" in filename or "\\" in filename or filename.startswith("."):
        return None
    if not filename.endswith(".json"):
        return None
    candidate = os.path.realpath(os.path.join(VORLAGEN_DIR, filename))
    # candidate muss exakt unter VORLAGEN_DIR liegen
    if not (candidate == VORLAGEN_DIR or candidate.startswith(VORLAGEN_DIR + os.sep)):
        logger.warning("Pfad-Traversal-Versuch geblockt: %r", filename)
        return None
    return candidate


def save_template(name: str, doc_type: str, fields: dict) -> dict:
    """Vorlage als JSON-Datei speichern."""
    filename = _sanitize_filename(name) + ".json"
    filepath = _safe_filepath(filename)
    if filepath is None:
        return {"success": False, "errors": ["Ungültiger Vorlagenname."]}

    data = {"name": name, "doc_type": doc_type, "fields": fields}

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        logger.exception("Vorlage konnte nicht gespeichert werden")
        return {"success": False, "errors": ["Vorlage konnte nicht gespeichert werden."]}

    return {"success": True, "filename": filename}


def list_templates() -> list:
    """Alle gespeicherten Vorlagen auflisten."""
    templates = []
    try:
        entries = sorted(os.listdir(VORLAGEN_DIR))
    except OSError:
        return templates
    for filename in entries:
        if not filename.endswith(".json"):
            continue
        filepath = _safe_filepath(filename)
        if filepath is None or not os.path.isfile(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            templates.append({
                "name":     data.get("name", filename),
                "doc_type": data.get("doc_type", ""),
                "filename": filename,
            })
        except (json.JSONDecodeError, IOError):
            continue
    return templates


def load_template(filename: str):
    """Eine Vorlage laden."""
    filepath = _safe_filepath(filename)
    if filepath is None or not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def delete_template(filename: str) -> bool:
    """Eine Vorlage löschen."""
    filepath = _safe_filepath(filename)
    if filepath is None or not os.path.isfile(filepath):
        return False
    try:
        os.remove(filepath)
        return True
    except OSError:
        logger.exception("Vorlage konnte nicht gelöscht werden")
        return False


def rename_template(filename: str, new_name: str):
    """Eine Vorlage umbenennen."""
    filepath = _safe_filepath(filename)
    if filepath is None or not os.path.isfile(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    new_filename = _sanitize_filename(new_name) + ".json"
    new_filepath = _safe_filepath(new_filename)
    if new_filepath is None:
        return None

    data["name"] = new_name

    try:
        with open(new_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        logger.exception("Vorlage konnte nicht umbenannt werden")
        return None

    if new_filepath != filepath and os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

    return {"success": True, "new_filename": new_filename}
