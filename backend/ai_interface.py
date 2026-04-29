"""
ai_interface.py – KI-Schnittstelle mit drei Pfaden

Reihenfolge der Versuche (priorisiert):
1. Groq Cloud-API (wenn die Umgebungsvariable GROQ_API_KEY gesetzt ist)
   – wird in der Render-/Workshop-Demo genutzt, schnell (~2 s).
2. Lokales Ollama (wenn unter http://localhost:11434 erreichbar)
   – datenschutzkonform, für die Lokal-Variante.
3. Regelbasierte Generierung
   – funktioniert immer, deterministisch, ohne Internet.

Die einzige öffentliche Funktion ist generate_document().
"""

import logging
import os
import requests

logger = logging.getLogger(__name__)

# ============================================================================
# KONFIGURATION
# ============================================================================

# --- Groq (Cloud) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT = 60

# --- Ollama (Lokal) ---
OLLAMA_URL     = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL   = os.environ.get("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = 120


# ============================================================================
# ÖFFENTLICHE FUNKTION
# ============================================================================

def generate_document(doc_type: str, data: dict) -> str:
    """Hauptfunktion: erzeugt einen Dokumententwurf.
    Probiert Groq → Ollama → Regel-Fallback in dieser Reihenfolge."""
    prompt = _build_prompt(doc_type, data)

    # 1. Groq versuchen (nur wenn API-Key vorhanden)
    if GROQ_API_KEY:
        try:
            return _generate_with_groq(prompt)
        except Exception as e:
            logger.warning("Groq-Aufruf fehlgeschlagen, versuche Ollama: %s", e)

    # 2. Lokales Ollama versuchen
    try:
        return _generate_with_ollama(prompt)
    except Exception as e:
        logger.info("Ollama nicht erreichbar, nutze Regel-Fallback: %s", e)

    # 3. Regelbasierter Fallback
    return _generate_with_rules(doc_type, data)


# ============================================================================
# GROQ (Cloud, OpenAI-kompatible API)
# ============================================================================

def _generate_with_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system",
             "content": "Du bist ein Assistent für den öffentlichen Dienst in Deutschland und formulierst Verwaltungsdokumente im sachlichen, behördlichen Stil. Du erfindest niemals Fakten, die nicht in den Eingabedaten stehen."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens":  2048,
        "stream":      False,
    }

    response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=GROQ_TIMEOUT)
    response.raise_for_status()
    result = response.json()

    text = result["choices"][0]["message"]["content"].strip()
    if not text:
        raise ValueError("Groq lieferte leeren Text")
    return text


# ============================================================================
# OLLAMA (Lokal)
# ============================================================================

def _generate_with_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model":   OLLAMA_MODEL,
            "prompt":  prompt,
            "stream":  False,
            "options": {"temperature": 0.4, "num_predict": 2048},
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    text = response.json().get("response", "").strip()
    if not text:
        raise ValueError("Ollama lieferte leeren Text")
    return text


# ============================================================================
# PROMPT-AUFBAU
# ============================================================================

def _build_prompt(doc_type: str, data: dict) -> str:
    """Erstellt einen optimierten Prompt für das LLM."""
    type_labels = {
        "aktenvermerk":          "einen formellen Aktenvermerk",
        "telefonnotiz":          "eine kompakte Telefonnotiz",
        "besprechungsprotokoll": "ein strukturiertes Besprechungsprotokoll",
    }

    type_structures = {
        "aktenvermerk": """Struktur:
- Kopfzeile mit Datum, Verfasser, Betreff
- 1. ANLASS (kurzer Einleitungssatz)
- 2. SACHVERHALT (Notizen als Fließtext formulieren)
- 3. ERGEBNIS / BEWERTUNG
- 4. WEITERE VERANLASSUNG (nächste Schritte)
- Fußzeile mit Datum und Verfasser""",

        "telefonnotiz": """Struktur:
- Kopfzeile mit Datum, Uhrzeit, Gesprächspartner, Betreff
- GESPRÄCHSINHALT (Notizen als zusammenhängenden Text formulieren)
- ERGEBNIS
- WIEDERVORLAGE / NÄCHSTE SCHRITTE
- Fußzeile mit Datum und Uhrzeit""",

        "besprechungsprotokoll": """Struktur:
- Kopfzeile mit Datum, Uhrzeit, Teilnehmer, Thema
- 1. TAGESORDNUNG / THEMA
- 2. BESPRECHUNGSINHALT (Notizen ausformulieren)
- 3. ERGEBNISSE / BESCHLÜSSE
- 4. TO-DOS / NÄCHSTE SCHRITTE (nummeriert)
- Fußzeile mit Datum und Teilnehmern""",
    }

    datum             = data.get("datum")              or "nicht angegeben"
    uhrzeit           = data.get("uhrzeit")            or "nicht angegeben"
    beteiligte        = data.get("beteiligte")         or "nicht angegeben"
    betreff           = data.get("betreff")            or "nicht angegeben"
    notizen           = data.get("notizen")            or "keine"
    naechste_schritte = data.get("naechste_schritte")  or "keine"

    return f"""Du bist ein Assistent für den öffentlichen Dienst in Deutschland.
Erstelle {type_labels.get(doc_type, "ein Dokument")} im sachlichen Verwaltungsstil.

{type_structures.get(doc_type, "")}

Eingabedaten:
- Datum: {datum}
- Uhrzeit: {uhrzeit}
- Beteiligte: {beteiligte}
- Betreff: {betreff}
- Notizen/Stichpunkte: {notizen}
- Nächste Schritte: {naechste_schritte}

Wichtige Regeln:
- Schreibe auf Deutsch in sachlichem, behördlichem Sprachstil.
- Formuliere die Stichpunkte zu vollständigen Sätzen aus.
- ERFINDE KEINE INHALTE, die nicht in den Eingabedaten stehen. Wenn ein Detail fehlt, lasse es weg oder verweise sachlich auf "nicht angegeben".
- Keine juristisch bindenden Zusagen formulieren.
- Keine Entscheidungen vorwegnehmen.
- Trennlinien mit "=" und "-" Zeichen verwenden.
- Am Ende: "Dokumentenstatus: Entwurf" einfügen.
- Gib NUR das fertige Dokument aus, keine Erklärungen davor oder danach."""


# ============================================================================
# REGELBASIERTE GENERIERUNG (Fallback)
# ============================================================================

def _generate_with_rules(doc_type: str, data: dict) -> str:
    """Regelbasierte Textgenerierung ohne KI."""
    datum             = data.get("datum")             or ""
    uhrzeit           = data.get("uhrzeit")           or ""
    beteiligte        = data.get("beteiligte")        or ""
    betreff           = data.get("betreff")           or ""
    naechste_schritte = data.get("naechste_schritte") or ""
    notizen           = data.get("notizen")           or ""

    notizen_text = _format_notes(notizen)

    if doc_type == "aktenvermerk":
        return _build_aktenvermerk(datum, beteiligte, betreff, notizen_text, naechste_schritte)
    elif doc_type == "telefonnotiz":
        return _build_telefonnotiz(datum, uhrzeit, beteiligte, betreff, notizen_text, naechste_schritte)
    elif doc_type == "besprechungsprotokoll":
        return _build_protokoll(datum, uhrzeit, beteiligte, betreff, notizen_text, naechste_schritte)
    else:
        return "Unbekannter Dokumenttyp."


def _format_notes(notizen: str) -> str:
    if not notizen.strip():
        return "Keine weiteren Angaben."
    lines = [line.strip() for line in notizen.strip().splitlines() if line.strip()]
    if len(lines) == 1:
        return lines[0]
    formatted = []
    for line in lines:
        if not line.startswith(("-", "•", "–", "*")):
            line = f"– {line}"
        formatted.append(line)
    return "\n".join(formatted)


def _build_aktenvermerk(datum, beteiligte, betreff, notizen, schritte) -> str:
    text = "AKTENVERMERK\n"
    text += "=" * 50 + "\n\n"
    text += f"Datum:       {datum}\n"
    text += f"Verfasser:   {beteiligte}\n"
    text += f"Betreff:     {betreff}\n\n"
    text += "-" * 50 + "\n\n"

    text += "1. ANLASS\n\n"
    text += f"   Der vorliegende Aktenvermerk dokumentiert den Sachverhalt\n"
    text += f"   zum Thema \"{betreff}\".\n\n"

    text += "2. SACHVERHALT\n\n"
    for line in notizen.splitlines():
        text += f"   {line}\n"
    text += "\n"

    text += "3. ERGEBNIS / BEWERTUNG\n\n"
    text += f"   Der Sachverhalt wurde zur Kenntnis genommen und dokumentiert.\n"
    text += f"   Eine weitergehende Prüfung bzw. Entscheidung obliegt der\n"
    text += f"   zuständigen Stelle.\n\n"

    text += "4. WEITERE VERANLASSUNG\n\n"
    if schritte.strip():
        for line in schritte.strip().splitlines():
            text += f"   – {line.strip()}\n"
    else:
        text += "   – Keine weiteren Maßnahmen erforderlich.\n"

    text += "\n" + "-" * 50 + "\n"
    text += f"Erstellt am {datum} | {beteiligte}\n"
    text += "Dokumentenstatus: Entwurf"

    return text


def _build_telefonnotiz(datum, uhrzeit, beteiligte, betreff, notizen, schritte) -> str:
    text = "TELEFONNOTIZ\n"
    text += "=" * 50 + "\n\n"
    text += f"Datum:             {datum}\n"
    text += f"Uhrzeit:           {uhrzeit}\n"
    text += f"Gesprächspartner:  {beteiligte}\n"
    text += f"Betreff:           {betreff}\n\n"
    text += "-" * 50 + "\n\n"

    text += "GESPRÄCHSINHALT:\n\n"
    for line in notizen.splitlines():
        text += f"   {line}\n"
    text += "\n"

    text += "ERGEBNIS:\n\n"
    text += f"   Das Gespräch wurde geführt. Die wesentlichen Punkte\n"
    text += f"   sind oben dokumentiert.\n\n"

    text += "WIEDERVORLAGE / NÄCHSTE SCHRITTE:\n\n"
    if schritte.strip():
        for line in schritte.strip().splitlines():
            text += f"   – {line.strip()}\n"
    else:
        text += "   – Keine Wiedervorlage erforderlich.\n"

    text += "\n" + "-" * 50 + "\n"
    text += f"Notiz erstellt am {datum}, {uhrzeit} Uhr\n"
    text += "Dokumentenstatus: Entwurf"

    return text


def _build_protokoll(datum, uhrzeit, beteiligte, betreff, notizen, schritte) -> str:
    text = "BESPRECHUNGSPROTOKOLL\n"
    text += "=" * 50 + "\n\n"
    text += f"Datum:        {datum}\n"
    text += f"Uhrzeit:      {uhrzeit}\n"
    text += f"Teilnehmer:   {beteiligte}\n"
    text += f"Thema:        {betreff}\n\n"
    text += "-" * 50 + "\n\n"

    text += "1. TAGESORDNUNG / THEMA\n\n"
    text += f"   Gegenstand der Besprechung: {betreff}\n\n"

    text += "2. BESPRECHUNGSINHALT\n\n"
    for line in notizen.splitlines():
        text += f"   {line}\n"
    text += "\n"

    text += "3. ERGEBNISSE / BESCHLÜSSE\n\n"
    text += f"   Die besprochenen Punkte wurden von den Teilnehmern\n"
    text += f"   zur Kenntnis genommen. Konkrete Beschlüsse und\n"
    text += f"   Zuständigkeiten ergeben sich aus den nachfolgenden\n"
    text += f"   Aufgaben.\n\n"

    text += "4. TO-DOS / NÄCHSTE SCHRITTE\n\n"
    if schritte.strip():
        for i, line in enumerate(schritte.strip().splitlines(), 1):
            text += f"   {i}. {line.strip()}\n"
    else:
        text += "   Keine offenen Aufgaben dokumentiert.\n"

    text += "\n" + "-" * 50 + "\n"
    text += f"Protokoll erstellt am {datum}\n"
    text += f"Teilnehmer: {beteiligte}\n"
    text += "Dokumentenstatus: Entwurf – zur Freigabe"

    return text
