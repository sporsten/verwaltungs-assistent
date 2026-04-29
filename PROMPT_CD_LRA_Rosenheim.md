# Prompt: Corporate Design Landratsamt Rosenheim umsetzen

> Diesen Prompt komplett in den Code-Assistenten kopieren.

---

## Ziel

Passe den Verwaltungs-Assistenten so an, dass sowohl die Web-Oberfläche als auch die generierten Dokumente (PDF und ggf. Word-Export) im Corporate Design des Landratsamts Rosenheim erscheinen. Als Referenz dient die Datei `Aktenvermerk Vorlage LRA Rosenheim.docx`, die im Projekt-Wurzelverzeichnis liegt.

## Referenzmaterial

- **Design-Vorlage:** `Aktenvermerk Vorlage LRA Rosenheim.docx` (im Projektordner)
- **Logo:** liegt eingebettet in der Vorlage unter `word/media/image1.jpeg` (798×255 px, grün-blaues Polygon-Motiv mit Schriftzug "LANDRATSAMT ROSENHEIM"). Bitte aus der Vorlage extrahieren und unter `frontend/static/lra_logo.jpg` (für die Web-UI) sowie `backend/assets/lra_logo.jpg` (für den PDF-Export) ablegen.

## Corporate-Design-Vorgaben (aus der Vorlage extrahiert)

| Element | Wert |
|---|---|
| Primärfarbe (Akzent, Linien, Überschriften) | `#FF6600` (Orange) |
| Sekundärfarbe (Metadaten, Hilfslinien) | `#808080` (Grau) |
| Textfarbe | `#000000` (Schwarz) |
| Hintergrund | `#FFFFFF` (Weiß) |
| Hauptschrift | Arial |
| Schriftgröße Fließtext | 11 pt |
| Schriftgröße Überschriften (H1) | 16 pt, fett |
| Schriftgröße Zwischenüberschriften (H2) | 12 pt, fett |

## Aufgaben

### 1. Web-Oberfläche (`frontend/`)

**`frontend/index.html`**
- Im Header das aktuelle Zahnrad-Icon (`&#9881;`) durch das LRA-Logo (`<img src="static/lra_logo.jpg" alt="Landratsamt Rosenheim">`) ersetzen.
- Den Titel "KI-Assistenzsystem für Verwaltungsdokumente" beibehalten, aber visuell unter/neben das Logo setzen.
- Subtitle "Prototyp – Projektstudie für den öffentlichen Dienst" beibehalten.
- Sicherstellen, dass die Datei `lra_logo.jpg` über die Flask-Static-Route ausgeliefert wird (ggf. in `app.py` `static_folder` setzen oder Datei in den existierenden Static-Ordner legen).

**`frontend/style.css`**
- Die CSS-Variablen in `:root` so ändern, dass das LRA-CD umgesetzt wird:
  ```css
  :root {
      --primary: #FF6600;        /* LRA Orange */
      --primary-light: #FF8533;
      --accent: #FF6600;
      --bg: #FFFFFF;             /* Weißer Hintergrund statt Hellgrau */
      --card-bg: #FFFFFF;
      --text: #000000;
      --text-light: #808080;     /* LRA Grau */
      --border: #CCCCCC;
      /* ... bestehende error/success/warning beibehalten ... */
  }
  ```
- `body { font-family: Arial, "Helvetica Neue", Helvetica, sans-serif; }` – Segoe UI durch Arial ersetzen.
- Header: weißer Hintergrund mit dünner orangefarbener Unterlinie (`border-bottom: 3px solid #FF6600;`), statt blauem Vollflächen-Header.
- H1/H2-Überschriften in Schwarz mit orangefarbenem Akzent (z. B. linker Border-Strich `border-left: 4px solid #FF6600; padding-left: 0.5rem;`).
- Buttons: Primärbutton mit Hintergrund `#FF6600`, Hover etwas dunkler (`#E55A00`), weißer Text.
- Form-Inputs: Border `#CCCCCC`, Focus-Border `#FF6600`.
- Karten (`.card`): weißer Hintergrund, dünner grauer Rahmen, kein Schatten oder nur sehr dezent.
- Prototyp-Banner: gelblicher Hintergrund beibehalten oder in dezentes Hellorange (`#FFF4E6`) mit orangefarbener linker Borderlinie.

### 2. PDF-Export (`backend/pdf_export.py`)

Die Datei nutzt aktuell `fpdf2` mit Helvetica und einem schlichten Layout. Bitte so umbauen, dass das generierte PDF **wie ein offizielles Aktenvermerk-Dokument des LRA Rosenheim aussieht**:

- **Kopfzeile auf Seite 1:** LRA-Logo links oben (Höhe ca. 25 mm, Breite proportional). Rechts daneben oder rechtsbündig: kleiner Verwaltungs-Header mit Geschäftszeichen-Platzhalter und Datum (im Stil der Vorlage). Unter dem Header eine dünne orange Trennlinie (`#FF6600`, ca. 0.5 mm).
- **Kopfzeile ab Seite 2:** Nur kleine Variante (Schriftzug "Landratsamt Rosenheim" rechts in Grau), keine Logo-Wiederholung.
- **Schrift:** Arial einbinden (TTF-Datei aus dem System oder per `add_font` als embedded Font, damit Umlaute korrekt dargestellt werden – Helvetica + Latin-1 wie bisher reicht nicht, sobald Sonderzeichen wie €, „" oder § vorkommen). Wenn keine TTF-Datei verfügbar ist, alternative wie DejaVuSans verwenden, aber sicherstellen, dass das Layout Arial-ähnlich wirkt.
- **Dokumenttitel** (z. B. "AKTENVERMERK"): Arial 16 pt fett, schwarz, linksbündig, mit orangefarbenem unteren Trennstrich.
- **Metadaten-Block** (Datum, Beteiligte, Betreff): zweispaltig in einer dezenten Tabellenoptik – Labels in Grau, Werte in Schwarz, Arial 10 pt.
- **Fließtext:** Arial 11 pt, Zeilenabstand ca. 1.4, Absatzabstand 4 mm.
- **Fußzeile:** linksbündig "Dokumentenstatus: Entwurf | KI-generiert – vor Ablage fachlich prüfen" in Grau (`#808080`), Arial 8 pt, rechtsbündig "Seite X/Y". Über der Fußzeile dünne graue Trennlinie.
- **Seitenränder:** oben 25 mm, unten 25 mm, links 25 mm, rechts 20 mm (entspricht typischer Bayerischer Verwaltungsformatierung).
- **Watermark/Hinweis:** Optional dezent quer über die erste Seite oder nur als Textzeile unter dem Titel: "KI-generierter Entwurf – vor Ablage fachlich prüfen".

### 3. Word-Export (.docx) – NEU implementieren

Ein Word-Export existiert bisher nicht (nur PDF). Bitte als zusätzliches Feature ergänzen:

**Backend (`backend/`)**
- Neues Modul `docx_export.py` anlegen, analog zu `pdf_export.py` aufgebaut.
- Bibliothek: **`python-docx`** verwenden (`pip install python-docx`, in `requirements.txt` ergänzen).
- Funktion `create_docx(text: str, doc_type: str, metadata: dict) -> bytes` exportieren, die ein vollständiges Word-Dokument als Bytes zurückgibt.
- In `app.py` einen neuen Endpoint `POST /api/export-docx` ergänzen, parallel zu `/api/export-pdf` – gleiche Eingabestruktur, Rückgabe als Datei-Download mit MIME-Type `application/vnd.openxmlformats-officedocument.wordprocessingml.document` und Dateiname-Schema `Aktenvermerk_YYYY-MM-DD.docx` (bzw. dokumenttyp-spezifisch).

**Layout des Word-Dokuments (visuell an `Aktenvermerk Vorlage LRA Rosenheim.docx` angelehnt)**
- Seitenformat A4, Ränder 25/20/25/25 mm (oben/rechts/unten/links).
- Standardschrift Arial, 11 pt.
- **Kopfzeile:** LRA-Logo links (Höhe ca. 25 mm), rechts ein kleiner Block mit Geschäftszeichen-Platzhalter (`Gz.: ____`) und Datum, Arial 9 pt grau. Darunter dünne orange Trennlinie (`#FF6600`).
- **Dokumenttitel:** "AKTENVERMERK" (bzw. "TELEFONNOTIZ", "BESPRECHUNGSPROTOKOLL"), Arial 16 pt fett, schwarz, mit orangefarbenem Trennstrich darunter.
- **Metadaten-Block:** zweispaltige unsichtbare Tabelle (Labels grau, Werte schwarz) für Datum, Uhrzeit, Beteiligte, Betreff.
- **Hauptteil:** Fließtext aus `text`-Parameter, Arial 11 pt, Zeilenabstand 1.4, Absatzabstand 4 mm. Wenn der Text strukturierte Abschnitte enthält ("Anlass", "Sachverhalt", "Ergebnis", "Nächste Schritte"), diese als H2-Zwischenüberschriften (Arial 12 pt fett schwarz, mit kleinem orange Akzentstrich davor) abbilden.
- **Fußzeile:** links "Dokumentenstatus: Entwurf | KI-generiert – vor Ablage fachlich prüfen" in Grau (`#808080`), Arial 8 pt; rechts Seitenzahl im Format "Seite X von Y". Über der Fußzeile dünne graue Trennlinie.
- **Hinweis-Box** unter dem Titel: heller Orange-Hintergrund (`#FFF4E6`) mit oranger linker Borderlinie und Text "KI-generierter Entwurf – vor Ablage fachlich prüfen.".
- Smart Quotes (typografische Anführungszeichen "..." und Apostrophe ') verwenden.

**Frontend (`frontend/`)**
- In `index.html` neben dem bestehenden "PDF herunterladen"-Button einen weiteren Button "Word herunterladen" ergänzen (gleiche Stilistik, ggf. mit kleinem Word-Icon `&#128196;` oder einfach Textbutton).
- In `script.js` analog zur PDF-Export-Funktion eine `exportDocx()`-Funktion ergänzen, die `POST /api/export-docx` aufruft und den Download triggert.
- Sicherstellen, dass beide Buttons (PDF und Word) erst aktiv werden, sobald ein Dokument generiert wurde.

### 4. Browser-Vorschau

Im Frontend gibt es bereits eine Live-Vorschau des generierten Dokuments. Diese Vorschau soll ebenfalls im neuen CD dargestellt werden (Logo oben, Arial, orangefarbener Akzentstrich), damit der Nutzer sieht, wie das spätere PDF aussieht. Die HTML-Struktur der Vorschau analog zum PDF aufbauen.

## Bedingungen

- **Bestehende Funktionalität nicht brechen:** Dokumentenerstellung, Vorlagen-Speichern, Beispieldaten, Spracheingabe-Knopf usw. müssen weiter funktionieren.
- **Drei Dokumenttypen:** Die Anpassung muss für Aktenvermerk, Telefonnotiz und Besprechungsprotokoll gelten.
- **Datenschutz-Hinweise behalten:** Der Hinweis "KI-generierter Entwurf – vor Ablage fachlich prüfen" bleibt sichtbar.
- **Logo-Lizenz:** Das Logo wird nur im Rahmen der Projektstudie/Demonstration verwendet. In `README.md` oder einer `LICENSE_NOTICE.md` einen kurzen Hinweis ergänzen, dass das LRA-Logo Eigentum des Landratsamts Rosenheim ist und im Prototyp nur zu Demonstrationszwecken eingesetzt wird.
- **Test:** Nach den Änderungen den Server neu starten, alle drei Dokumenttypen einmal mit Beispieldaten generieren, das PDF herunterladen und mit der Vorlage `Aktenvermerk Vorlage LRA Rosenheim.docx` visuell abgleichen.

## Reihenfolge der Umsetzung (Vorschlag)

1. Logo aus der Vorlage extrahieren und in `frontend/static/` und `backend/assets/` ablegen.
2. `frontend/style.css` und `frontend/index.html` umstellen → im Browser prüfen.
3. `backend/pdf_export.py` anpassen → ein PDF generieren und visuell mit der Vorlage vergleichen.
4. Neues Modul `backend/docx_export.py` anlegen, Endpoint `/api/export-docx` in `app.py` einbauen, Frontend-Button und JS-Funktion ergänzen → ein Word-Dokument generieren und in Word/LibreOffice öffnen, visuell mit der Vorlage abgleichen.
5. Live-Vorschau im Frontend an das neue Layout angleichen.
6. README/LICENSE-Hinweis ergänzen, kurze Zusammenfassung der Änderungen am Ende ausgeben.

## Abschluss

Bitte im Chat eine kurze Zusammenfassung der geänderten Dateien und der getesteten Dokumenttypen liefern, sowie eine Beschreibung der Header-Optik (vorher/nachher). Falls Annahmen getroffen werden mussten (z. B. wegen fehlender Schrift-Datei), diese explizit auflisten.

## Zusammenfassungs-Dokument erstellen (Pflicht)

Erstelle nach Abschluss aller Änderungen zusätzlich eine Zusammenfassung als **Word-Dokument** und lege sie im Projekt-Wurzelverzeichnis ab:

- **Dateiname:** `CD_LRA_Rosenheim_Zusammenfassung.docx`
- **Stil:** analog zu den vorhandenen Zusammenfassungen im selben Ordner (`Deployment_Zusammenfassung.docx`, `PDF_Export_Zusammenfassung.docx`, `Projektstudie_LLM_Integration.docx` usw.) – Arial, H1 dunkelblau (`#1F3864`) fett 18 pt, H2 mittelblau (`#2E75B6`) fett 14 pt, Fließtext 11 pt, Tabellen mit blauer Headerzeile und alternierenden hellen Zeilen, A4 mit 1-Zoll-Rändern, Fußzeile mit Seitenzahl.
- **Mindestens diese Abschnitte:**
  1. **Ziel der Anpassung** – kurze Beschreibung, warum das Corporate Design des LRA Rosenheim umgesetzt wurde.
  2. **Designvorgaben** – Tabelle mit den verwendeten Farben (`#FF6600`, `#808080`), Schriftarten und Layout-Regeln.
  3. **Geänderte Dateien** – Tabelle: Datei | Art der Änderung. Alle berührten Dateien aus `frontend/` und `backend/` auflisten.
  4. **Neue Komponenten** – speziell der Word-Export (`backend/docx_export.py`, neuer Endpoint, neuer Button im Frontend).
  5. **PDF-Export-Anpassung** – Beschreibung, was am bestehenden PDF-Export geändert wurde.
  6. **Web-Oberfläche** – Beschreibung der Header-Umstellung (Logo statt Zahnrad, Arial, orangefarbene Akzente).
  7. **Logo-Hinweis** – kurzer Absatz zur Verwendung des LRA-Logos im Rahmen der Projektstudie.
  8. **Test-Ergebnis** – welche Dokumenttypen wurden mit Beispieldaten getestet, was war das Ergebnis (PDF und Word geöffnet, Layout passt zur Vorlage).
  9. **Bekannte Einschränkungen / Annahmen** – falls Schriften, Bibliotheken o. Ä. nicht 1:1 verfügbar waren.
- Wenn `python-docx` ohnehin neu im Projekt installiert wurde, kannst du dieses Dokument direkt damit erzeugen.
