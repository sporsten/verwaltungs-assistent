"""
document_logic.py – Dokumentlogik und Validierung

Dieses Modul enthält:
- Validierung der Eingabedaten
- Beispieldaten für den Schnelltest
- Koordination zwischen Eingabe und KI-Schnittstelle

Es bildet die Brücke zwischen der Flask-API und der KI-Generierung.
"""

from ai_interface import generate_document


# ============================================================================
# VALIDIERUNG
# ============================================================================

# Pflichtfelder je Dokumenttyp
REQUIRED_FIELDS = {
    "aktenvermerk": {
        "datum": "Bitte ein Datum angeben.",
        "beteiligte": "Bitte den Verfasser / die Beteiligten angeben.",
        "betreff": "Bitte einen Betreff oder Anlass angeben.",
        "notizen": "Bitte Stichpunkte oder Notizen zum Sachverhalt eingeben."
    },
    "telefonnotiz": {
        "datum": "Bitte das Datum des Gesprächs angeben.",
        "uhrzeit": "Bitte die Uhrzeit des Gesprächs angeben.",
        "beteiligte": "Bitte den Gesprächspartner angeben.",
        "notizen": "Bitte den Gesprächsinhalt stichpunktartig eingeben."
    },
    "besprechungsprotokoll": {
        "datum": "Bitte das Datum der Besprechung angeben.",
        "beteiligte": "Bitte die Teilnehmer angeben.",
        "betreff": "Bitte das Thema der Besprechung angeben.",
        "notizen": "Bitte den Besprechungsinhalt eingeben."
    }
}

VALID_DOC_TYPES = ["aktenvermerk", "telefonnotiz", "besprechungsprotokoll"]


def validate_input(doc_type: str, data: dict) -> list:
    """
    Prüft die Eingabedaten auf Vollständigkeit.

    Rückgabe:
        Liste mit Fehlermeldungen (leer = alles OK)
    """
    errors = []

    if doc_type not in VALID_DOC_TYPES:
        errors.append("Bitte einen gültigen Dokumenttyp auswählen.")
        return errors

    required = REQUIRED_FIELDS.get(doc_type, {})
    for field, message in required.items():
        value = (data.get(field) or "").strip()
        if not value:
            errors.append(message)

    return errors


def create_document(doc_type: str, data: dict) -> dict:
    """
    Erstellt ein Dokument nach Validierung.

    Rückgabe:
        Dict mit "success", "text" oder "errors"
    """
    # Validierung
    errors = validate_input(doc_type, data)
    if errors:
        return {"success": False, "errors": errors}

    # Dokument generieren (über KI-Schnittstelle)
    text = generate_document(doc_type, data)

    return {"success": True, "text": text}


# ============================================================================
# BEISPIELDATEN für Schnelltest
# ============================================================================

EXAMPLE_DATA = {
    "aktenvermerk": {
        "datum": "12.03.2026",
        "uhrzeit": "",
        "beteiligte": "Müller, Sachgebiet 3.1",
        "betreff": "Überprüfung der Raumvergabe im Verwaltungsgebäude II",
        "notizen": "Raumvergabe für Q2 steht noch aus\nZwei Abteilungen haben Überschneidungen gemeldet\nGebäudemanagement wurde informiert\nVorschlag: Gemeinsamer Termin zur Abstimmung",
        "naechste_schritte": "Termin mit Gebäudemanagement bis KW 12 vereinbaren\nRaumplan aktualisieren\nRückmeldung an Abteilungen 2.3 und 4.1"
    },
    "telefonnotiz": {
        "datum": "12.03.2026",
        "uhrzeit": "10:30",
        "beteiligte": "Frau Schmidt, Bürgeramt Süd",
        "betreff": "Rückfrage zur Bearbeitungsdauer Antrag Nr. 2024-4471",
        "notizen": "Frau Schmidt fragt nach dem Stand des Antrags\nAntrag liegt seit 4 Wochen in Prüfung\nFehlende Unterlage: Meldebescheinigung\nBittet um Rückruf nach Klärung",
        "naechste_schritte": "Fehlende Unterlage bei Antragsteller anfordern\nRückruf an Frau Schmidt bis Freitag"
    },
    "besprechungsprotokoll": {
        "datum": "12.03.2026",
        "uhrzeit": "14:00",
        "beteiligte": "Herr Weber (Leitung), Frau Koch (SG 2.1), Herr Yilmaz (IT), Frau Braun (Personal)",
        "betreff": "Einführung digitale Zeiterfassung",
        "notizen": "Aktuelles System wird zum 30.06. abgeschaltet\nNeue Software wurde in Abt. 3 getestet\nPositives Feedback, aber Schulungsbedarf\nDatenschutz-Folgenabschätzung steht noch aus\nRollout für alle Abteilungen ab September geplant",
        "naechste_schritte": "IT erstellt Schulungskonzept bis KW 15\nDatenschutzbeauftragten einbeziehen\nTestphase in Abt. 1 und 5 ab Mai\nInfo-Rundmail an alle Beschäftigten"
    }
}


def get_example_data(doc_type: str) -> dict:
    """Gibt Beispieldaten für den gewählten Dokumenttyp zurück."""
    return EXAMPLE_DATA.get(doc_type, EXAMPLE_DATA["aktenvermerk"])
