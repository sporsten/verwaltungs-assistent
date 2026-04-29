# KI-Assistenzsystem für Verwaltungsdokumente

**Prototyp – Projektstudie für den öffentlichen Dienst**

---

## Ziel der Anwendung

Dieses System unterstützt Sachbearbeiterinnen und Sachbearbeiter sowie Assistenzkräfte im öffentlichen Dienst bei der Erstellung standardisierter Verwaltungsdokumente:

- **Aktenvermerke** – formelle Dokumentation von Sachverhalten
- **Telefonnotizen** – kompakte Gesprächsdokumentation
- **Besprechungsprotokolle** – strukturierte Ergebnissicherung

Die Anwendung erstellt auf Basis von Stichpunkten einen formulierten Entwurf im sachlichen Verwaltungsstil. Der Entwurf wird anschließend von der Fachkraft geprüft und ggf. angepasst.

## Nutzen im öffentlichen Dienst

- **Zeitersparnis** bei wiederkehrenden Dokumentationsaufgaben
- **Einheitliche Struktur** durch vordefinierte Dokumentformate
- **Qualitätssicherung** durch konsistente Formulierungen
- **Niedrige Einstiegshürde** – einfache Bedienung ohne Schulungsaufwand
- **Mensch bleibt in Kontrolle** – KI erstellt nur einen Entwurf

## Zwei Betriebsmodi

Diese Anwendung unterstützt bewusst zwei Betriebsmodi:

### 1. Workshop-Demo (öffentliche Cloud, [verwaltungs-assistent.onrender.com](https://verwaltungs-assistent.onrender.com))

- Gehostet auf Render Free Tier (Cloud-Dienst, EU/US-Region).
- Zur **schnellen Erprobung im Workshop** durch externe Tester:innen ohne Installationsaufwand.
- KI-Generierung läuft über eine **kostenfreie LLM-API (Groq)** – Daten verlassen den lokalen Rechner.
- Spracheingabe nutzt die **Web Speech API des Browsers** (in Chrome ggf. Google-Backend).
- **Nur fingierte Beispieldaten verwenden!** Keine echten personenbezogenen Vorgangsdaten.
- Cold-Start: Der Server schläft nach 15 Min Inaktivität ein und braucht ca. 50 Sek. zum Aufwachen.

### 2. Lokale Variante (produktionsnaher Datenschutz)

- Komplett auf dem eigenen Rechner – **keine Daten verlassen das Gerät**.
- LLM-Generierung über **lokales Ollama** (z. B. `llama3.2`).
- Spracherkennung über **lokales `faster-whisper`-Modell**.
- Templates werden lokal als JSON gespeichert.
- Empfohlene Variante für reale Verwaltungsdaten und für den dauerhaften Einsatz.

> **Wichtig für die Projektstudie:** Die Cloud-Demo dient nur dem niedrigschwelligen Test im Workshop. Im realen Verwaltungsbetrieb müsste die lokale Variante (ggf. mit DMS-Anbindung, GoBD-konformer Ablage und Aktenzeichenvergabe) eingesetzt werden. Siehe Abschnitt „Mögliche Erweiterungen".

---

## Startanleitung

### Voraussetzungen

- Python 3.9 oder neuer (Download: https://www.python.org/downloads/)

### Installation und Start

1. **Terminal öffnen** (PowerShell oder Eingabeaufforderung)

2. **In den Projektordner wechseln:**
   ```
   cd verwaltungs-assistent
   ```

3. **Abhängigkeiten installieren:**
   ```
   pip install -r backend/requirements.txt
   ```

4. **Server starten:**
   ```
   python backend/app.py
   ```

5. **Browser öffnen:**
   ```
   http://localhost:5000
   ```

6. **Beenden:** Im Terminal `Strg + C` drücken.

---

## Projektstruktur

```
verwaltungs-assistent/
├── backend/
│   ├── app.py              # Flask-Server und API-Endpunkte
│   ├── document_logic.py   # Validierung und Dokumenterstellung
│   ├── ai_interface.py     # KI-Schnittstelle (austauschbar)
│   └── requirements.txt    # Python-Abhängigkeiten
├── frontend/
│   ├── index.html          # Benutzeroberfläche
│   ├── style.css           # Design
│   └── script.js           # Frontend-Logik
└── README.md               # Diese Datei
```

### Architekturprinzip

Die Anwendung ist in drei Schichten getrennt:

1. **Frontend** (HTML/CSS/JS) – Benutzeroberfläche
2. **Dokumentlogik** (document_logic.py) – Validierung und Steuerung
3. **KI-Schnittstelle** (ai_interface.py) – Textgenerierung (austauschbar)

Die KI-Schnittstelle ist bewusst als eigenständiges Modul umgesetzt. Aktuell arbeitet sie regelbasiert. Später kann sie durch ein lokales LLM oder eine API ersetzt werden – ohne Änderungen am Rest der Anwendung.

---

## Mögliche Erweiterungen (Version 2)

| Feature | Beschreibung |
|---|---|
| ~~Lokales LLM~~ | *(umgesetzt – Ollama mit llama3.2)* |
| ~~Spracheingabe~~ | *(umgesetzt – lokale Erkennung mit faster-whisper)* |
| ~~PDF-Export~~ | *(umgesetzt – fpdf2)* |
| Vorlagen | Eigene Dokumentvorlagen speichern und laden |
| Versionierung | Änderungshistorie für Dokumente |
| Mehrsprachigkeit | Unterstützung weiterer Sprachen |
| Benutzerverwaltung | Login und persönliche Einstellungen |
| Aktenzeichen | Automatische Vergabe und Verwaltung |

---

## Technologie

| Komponente | Technologie | Begründung |
|---|---|---|
| Backend | Python + Flask | Minimaler Aufwand, schnell aufgesetzt, gute Erweiterbarkeit |
| Frontend | HTML + CSS + JS | Keine Build-Tools nötig, sofort lauffähig |
| KI-Text | Ollama (llama3.2) | Lokales LLM, datenschutzkonform, mit regelbasiertem Fallback |
| KI-Sprache | faster-whisper | Lokale Spracherkennung, kein Cloud-Upload |

---

---

## Lizenz- und Bildrechte

Das LRA-Logo ist Eigentum des Landratsamts Rosenheim und wird im Prototyp nur zu Demonstrationszwecken im Rahmen der Projektstudie verwendet. Eine kommerzielle Nutzung oder Weitergabe des Logos ist ohne ausdrückliche Genehmigung des Landratsamts Rosenheim nicht gestattet.

---

*Erstellt im Rahmen einer Projektstudie – März 2026*
