"""
speech_to_text.py – Spracherkennung & Feldextraktion

Zwei Modi:
- Lokal: faster-whisper (Audio → Text), Ollama (Text → Felder)
- Cloud (Render/Workshop): Web Speech API im Browser liefert Text direkt;
  /api/transcribe wird dann nur als Fallback gerufen.

Damit der Server auch ohne installiertes faster-whisper startet
(z. B. auf Render Free Tier, das die ~1,5 GB Modelldatei nicht stemmt),
wird WhisperModel erst beim ersten Aufruf importiert.
"""

import json
import logging
import os
import tempfile

import requests as http_requests

logger = logging.getLogger(__name__)

# ============================================================================
# WHISPER (lokale Spracherkennung)
# ============================================================================

WHISPER_MODEL_SIZE   = os.environ.get("WHISPER_MODEL_SIZE", "medium")
WHISPER_DEVICE       = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

_model = None


def _get_model():
    """Lazy Import + Lazy Load: Modell wird erst beim ersten Aufruf geholt.
    So startet der Server auch ohne faster-whisper-Paket."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Audio-Bytes → erkannter deutscher Text."""
    suffix = os.path.splitext(filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = _get_model()
        segments, _info = model.transcribe(
            tmp_path,
            language="de",
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(segment.text.strip() for segment in segments)
        return text.strip()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ============================================================================
# STRUKTURIERTE FELDEXTRAKTION (Groq → Ollama → Fallback)
# ============================================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")


def extract_fields(raw_text: str, doc_type: str) -> dict:
    """Diktierten Text in strukturierte Formularfelder zerlegen.
    Versucht Groq → Ollama → Fallback (alles in 'notizen')."""
    fallback = {
        "datum": "",
        "uhrzeit": "",
        "beteiligte": "",
        "betreff": "",
        "notizen": raw_text,
        "naechste_schritte": "",
    }

    type_labels = {
        "aktenvermerk":          "Aktenvermerk",
        "telefonnotiz":          "Telefonnotiz",
        "besprechungsprotokoll": "Besprechungsprotokoll",
    }

    prompt = f"""Analysiere den folgenden diktierten Text und extrahiere die Informationen in ein JSON-Objekt.
Der Text wurde für ein Verwaltungsdokument vom Typ "{type_labels.get(doc_type, "Dokument")}" diktiert.

Diktierter Text:
"{raw_text}"

Extrahiere folgende Felder (leer lassen wenn nicht erkennbar):
- datum: Datum im Format TT.MM.JJJJ
- uhrzeit: Uhrzeit im Format HH:MM
- beteiligte: Namen der beteiligten Personen
- betreff: Thema oder Anlass
- notizen: Die inhaltlichen Stichpunkte (je Punkt eine neue Zeile)
- naechste_schritte: Aufgaben, To-dos, Wiedervorlagen (je Punkt eine neue Zeile)

Erfinde KEINE Inhalte, die nicht im Text stehen.
Antworte NUR mit dem JSON-Objekt, keine Erklärung davor oder danach.
Beispiel-Format:
{{"datum": "15.03.2026", "uhrzeit": "10:00", "beteiligte": "Herr Müller", "betreff": "Raumvergabe", "notizen": "Punkt 1\\nPunkt 2", "naechste_schritte": "Aufgabe 1"}}"""

    # 1. Groq versuchen
    if GROQ_API_KEY:
        try:
            return _extract_with_groq(prompt, fallback)
        except Exception as e:
            logger.warning("Groq-Extraktion fehlgeschlagen, versuche Ollama: %s", e)

    # 2. Ollama versuchen
    try:
        return _extract_with_ollama(prompt, fallback)
    except Exception as e:
        logger.info("Ollama-Extraktion nicht verfügbar, nutze Fallback: %s", e)

    # 3. Fallback: alles in Notizen
    return fallback


def _extract_with_groq(prompt: str, fallback: dict) -> dict:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Du bist ein präziser Daten-Extraktor und antwortest ausschließlich mit gültigem JSON."},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens":  1024,
        "response_format": {"type": "json_object"},
    }
    r = http_requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]
    return _parse_json_safely(raw, fallback)


def _extract_with_ollama(prompt: str, fallback: dict) -> dict:
    r = http_requests.post(
        OLLAMA_URL,
        json={
            "model":   OLLAMA_MODEL,
            "prompt":  prompt,
            "stream":  False,
            "options": {"temperature": 0.1, "num_predict": 1024},
        },
        timeout=60,
    )
    r.raise_for_status()
    raw = r.json().get("response", "")
    return _parse_json_safely(raw, fallback)


def _parse_json_safely(raw: str, fallback: dict) -> dict:
    """JSON aus einem LLM-Output extrahieren – robust gegen Vor-/Nachtext."""
    raw = (raw or "").strip()
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start < 0 or end <= start:
        return fallback
    try:
        fields = json.loads(raw[start:end])
    except json.JSONDecodeError:
        return fallback
    # Sicherstellen, dass alle erwarteten Felder existieren
    for key in fallback:
        if key not in fields or not isinstance(fields[key], str):
            fields[key] = fallback[key] if key == "notizen" else ""
    return fields
