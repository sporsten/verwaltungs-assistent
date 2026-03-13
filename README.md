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

## Datenschutz-Hinweis

- Die Anwendung läuft **vollständig lokal** auf dem eigenen Rechner
- Es werden **keine Daten an externe Server** übermittelt
- Keine Cloud-Anbindung, keine Registrierung, keine Nutzerdaten
- Bei einer späteren LLM-Anbindung wird ein **lokales Modell** empfohlen (z. B. Ollama), um den Datenschutz zu gewährleisten
- Die Architektur ist so gestaltet, dass der Datenschutz auch bei Erweiterungen gewahrt bleibt

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
| Lokales LLM | Anbindung z. B. über Ollama für natürlichere Textgenerierung |
| Spracheingabe | Diktierfunktion über Web Speech API |
| PDF-Export | Dokumente als PDF herunterladen |
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
| KI | Regelbasiert (Mock) | Prototyp ohne externe Abhängigkeit, LLM-ready |

---

*Erstellt im Rahmen einer Projektstudie – März 2026*
