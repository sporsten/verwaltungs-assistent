"""
ai_interface.py – KI-Schnittstelle (Platzhalter für spätere LLM-Anbindung)

Dieses Modul kapselt die gesamte KI-Logik.
Aktuell wird eine regelbasierte Textgenerierung verwendet.
Später kann hier ein lokales LLM (z.B. Ollama, llama.cpp) oder
eine API (z.B. OpenAI, Anthropic) angebunden werden.

Architektur:
- generate_document() ist die einzige öffentliche Funktion
- Intern wird entschieden, ob Mock oder echtes LLM genutzt wird
- Das Backend ruft nur diese Funktion auf → Austausch ohne Codeänderung möglich
"""

# ============================================================================
# KONFIGURATION – Hier einstellen, welche KI-Engine verwendet wird
# ============================================================================

# Auf "llm" umstellen, sobald ein echtes Modell angebunden ist
AI_MODE = "mock"  # "mock" = regelbasiert, "llm" = echtes Sprachmodell


def generate_document(doc_type: str, data: dict) -> str:
    """
    Hauptfunktion: Erzeugt einen Dokumententwurf.

    Parameter:
        doc_type: "aktenvermerk", "telefonnotiz" oder "besprechungsprotokoll"
        data: Dict mit den Eingabefeldern (datum, uhrzeit, beteiligte, etc.)

    Rückgabe:
        Formatierter Dokumenttext als String
    """
    if AI_MODE == "llm":
        return _generate_with_llm(doc_type, data)
    else:
        return _generate_with_rules(doc_type, data)


# ============================================================================
# REGELBASIERTE GENERIERUNG (aktuell aktiv)
# ============================================================================

def _generate_with_rules(doc_type: str, data: dict) -> str:
    """Regelbasierte Textgenerierung ohne KI."""

    datum = data.get("datum", "")
    uhrzeit = data.get("uhrzeit", "")
    beteiligte = data.get("beteiligte", "")
    betreff = data.get("betreff", "")
    naechste_schritte = data.get("naechste_schritte", "")
    notizen = data.get("notizen", "")

    # Notizen aufbereiten: Stichpunkte zu Fließtext
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
    """Formatiert Rohnotizen zu lesbarem Text."""
    if not notizen.strip():
        return "Keine weiteren Angaben."

    lines = [line.strip() for line in notizen.strip().splitlines() if line.strip()]

    if len(lines) == 1:
        return lines[0]

    # Mehrere Stichpunkte als Aufzählung
    formatted = []
    for line in lines:
        # Vorhandene Aufzählungszeichen beibehalten oder hinzufügen
        if not line.startswith(("-", "•", "–", "*")):
            line = f"– {line}"
        formatted.append(line)
    return "\n".join(formatted)


def _build_aktenvermerk(datum, beteiligte, betreff, notizen, schritte) -> str:
    """Erstellt einen formellen Aktenvermerk."""
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
    """Erstellt eine kompakte Telefonnotiz."""
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
    """Erstellt ein strukturiertes Besprechungsprotokoll."""
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


# ============================================================================
# LLM-ANBINDUNG (Platzhalter für spätere Implementierung)
# ============================================================================
#
# ANLEITUNG FÜR DIE LLM-INTEGRATION:
#
# 1. Option A: Lokales LLM (z.B. Ollama)
#    - Ollama installieren: https://ollama.ai
#    - Modell laden: ollama pull llama3
#    - URL unten anpassen auf http://localhost:11434/api/generate
#
# 2. Option B: API-Anbindung (z.B. OpenAI, Anthropic)
#    - API-Key als Umgebungsvariable setzen
#    - Entsprechende Python-Bibliothek installieren
#
# 3. AI_MODE oben auf "llm" umstellen
#
# DATENSCHUTZ-HINWEIS:
# Bei Verwendung externer APIs werden Daten an Dritte übermittelt.
# Für den öffentlichen Dienst wird ein lokales LLM empfohlen.
# ============================================================================

def _generate_with_llm(doc_type: str, data: dict) -> str:
    """
    Platzhalter für echte LLM-Generierung.

    TODO: Hier die gewünschte LLM-Bibliothek importieren und nutzen.
    Beispiel für Ollama:

        import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": _build_prompt(doc_type, data),
                "stream": False
            }
        )
        return response.json()["response"]

    Beispiel für Anthropic Claude API:

        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": _build_prompt(doc_type, data)}]
        )
        return message.content[0].text
    """
    # Fallback auf regelbasierte Generierung, bis LLM konfiguriert ist
    return _generate_with_rules(doc_type, data)


def _build_prompt(doc_type: str, data: dict) -> str:
    """
    Erstellt einen Prompt für das LLM.
    Wird erst genutzt, wenn AI_MODE auf "llm" steht.
    """
    type_labels = {
        "aktenvermerk": "einen formellen Aktenvermerk",
        "telefonnotiz": "eine kompakte Telefonnotiz",
        "besprechungsprotokoll": "ein strukturiertes Besprechungsprotokoll"
    }

    prompt = f"""Du bist ein Assistent für den öffentlichen Dienst.
Erstelle {type_labels.get(doc_type, 'ein Dokument')} im sachlichen Verwaltungsstil.

Eingabedaten:
- Datum: {data.get('datum', 'nicht angegeben')}
- Uhrzeit: {data.get('uhrzeit', 'nicht angegeben')}
- Beteiligte: {data.get('beteiligte', 'nicht angegeben')}
- Betreff: {data.get('betreff', 'nicht angegeben')}
- Notizen: {data.get('notizen', 'keine')}
- Nächste Schritte: {data.get('naechste_schritte', 'keine')}

Wichtige Regeln:
- Sachlicher, behördlicher Sprachstil
- Keine juristisch bindenden Zusagen formulieren
- Keine Entscheidungen vorwegnehmen
- Hinweis auf Entwurfsstatus einfügen
"""
    return prompt
