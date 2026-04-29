# Sitzung 2 – CD-Umstellung Verwaltungs-Assistent (Fortsetzung)

Die Web-Oberfläche wurde in Sitzung 1 bereits komplett auf das LRA-Corporate-Design umgestellt. **Jetzt fehlen noch Backend (PDF + Word) sowie Tests und Zusammenfassung.**

## Was in Sitzung 1 schon erledigt ist

- LRA-Logo extrahiert und abgelegt unter:
  - `frontend/static/lra_logo.jpg`
  - `backend/assets/lra_logo.jpg`
- `frontend/index.html`: Zahnrad → LRA-Logo im Header, Word-Button zusätzlich zum PDF-Button, neue „Briefbogen"-Vorschau-Box (`.preview-paper`) oberhalb des Output-Textfelds.
- `frontend/style.css`: komplett neu im LRA-CD (Orange #FF6600, Grau #808080, Arial, weißer Header mit oranger Trennlinie, Karten ohne Schatten, Preview-Paper-Stile).
- `frontend/script.js`: neue Funktion `updatePreviewPaper(docType, datum)` setzt Titel + Datum im Briefbogen-Header. Neue Funktion `downloadDOCX()` ruft `POST /api/export-docx` auf — **dieser Endpoint existiert noch NICHT, muss in Sitzung 2 angelegt werden.**

## Aufgaben Sitzung 2

### 1. PDF-Export im LRA-CD neu (`backend/pdf_export.py`)
Datei nutzt aktuell fpdf2 mit Helvetica. Bitte umbauen:
- Logo aus `backend/assets/lra_logo.jpg` links oben (Höhe ca. 25 mm).
- Rechts oben grauer Mini-Header: „Gz.: ____" + Datum, Arial-ähnlich (DejaVuSans falls Arial nicht verfügbar), 9 pt grau (#808080).
- Unter dem Header dünne orange Trennlinie (#FF6600, 0.5 mm).
- Ab Seite 2: nur kleiner Schriftzug „Landratsamt Rosenheim" rechtsbündig in Grau, kein Logo.
- Dokumenttitel („AKTENVERMERK" / „TELEFONNOTIZ" / „BESPRECHUNGSPROTOKOLL") 16 pt fett schwarz mit orangem Trennstrich darunter.
- Hinweiszeile unter Titel: „KI-generierter Entwurf – vor Ablage fachlich prüfen" in Grau.
- Fließtext 11 pt, Zeilenabstand ~1.4.
- Fußzeile: links „Dokumentenstatus: Entwurf | KI-generiert – vor Ablage fachlich prüfen" Grau 8 pt, rechts „Seite X/Y", darüber dünne graue Trennlinie.
- Ränder: oben/links 25 mm, unten 25 mm, rechts 20 mm.
- Schrift: TTF einbinden (DejaVuSans aus `C:\Windows\Fonts` oder fpdf2-eigene), damit Umlaute/€/§ korrekt rauskommen.

### 2. Word-Export NEU (`backend/docx_export.py`)
- Bibliothek: `python-docx` (in `backend/requirements.txt` UND `requirements.txt` im Projekt-Root ergänzen).
- Funktion: `create_docx(text: str, doc_type: str, metadata: dict) -> bytes`
- Layout analog zum PDF: A4, Ränder 25/20/25/25 mm, Arial 11 pt, Logo-Header mit Gz./Datum rechts, oranger Trennlinie, Titel 16 pt fett mit orangem Akzentstrich, Metadaten-Block als zweispaltige unsichtbare Tabelle (Labels grau, Werte schwarz), Hinweis-Box (heller Orange-Hintergrund #FFF4E6 mit oranger linker Border), Fließtext mit Zwischenüberschriften (H2 Arial 12 pt fett), Fußzeile mit Status-Text + Seitenzahl.
- Smart Quotes (typografische Anführungszeichen) verwenden.

### 3. Endpoint in `backend/app.py`
- Neuer Route `POST /api/export-docx`, parallel zu `/api/export-pdf`.
- Eingang: `{ text, doc_type, metadata }` (Frontend schickt das schon so).
- Rückgabe: Datei-Download, MIME `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, Filename `{Aktenvermerk|Telefonnotiz|Besprechungsprotokoll}_YYYY-MM-DD.docx`.

### 4. README + Lizenz-Hinweis
- In `README.md` (oder neuer `LICENSE_NOTICE.md`) einen Absatz: „Das LRA-Logo ist Eigentum des Landratsamts Rosenheim und wird im Prototyp nur zu Demonstrationszwecken im Rahmen der Projektstudie verwendet."

### 5. Test
- Server starten: `py backend/app.py`
- Alle drei Dokumenttypen (Aktenvermerk, Telefonnotiz, Besprechungsprotokoll) mit Beispieldaten generieren.
- PDF + Word herunterladen, beide öffnen, mit `Aktenvermerk Vorlage LRA Rosenheim.docx` abgleichen.

### 6. Zusammenfassungs-Dokument (Pflicht)
- Datei: `CD_LRA_Rosenheim_Zusammenfassung.docx` im Projekt-Wurzelverzeichnis.
- Stil analog zu `Deployment_Zusammenfassung.docx` etc.: Arial, H1 #1F3864 fett 18 pt, H2 #2E75B6 fett 14 pt, Fließtext 11 pt, Tabellen mit blauer Headerzeile, A4 mit 1-Zoll-Rändern, Fußzeile mit Seitenzahl.
- Abschnitte: Ziel der Anpassung, Designvorgaben (Tabelle Farben/Schriften), Geänderte Dateien (Tabelle Datei | Art der Änderung), Neue Komponenten (Word-Export), PDF-Anpassung, Web-Oberfläche (Header vorher/nachher), Logo-Hinweis, Test-Ergebnis, Bekannte Einschränkungen/Annahmen.

## Bedingungen (gelten weiter)
- Bestehende Funktionen nicht brechen (Templates, Beispieldaten, Spracheingabe).
- Hinweis „KI-generierter Entwurf – vor Ablage fachlich prüfen" muss überall sichtbar bleiben.
- Token-sparend arbeiten, parallel wo möglich.

## Referenzdateien im Projekt
- Vorlage: `Aktenvermerk Vorlage LRA Rosenheim.docx`
- Logo: `backend/assets/lra_logo.jpg`
- Stil-Referenz für Zusammenfassung: `Deployment_Zusammenfassung.docx`, `PDF_Export_Zusammenfassung.docx`
