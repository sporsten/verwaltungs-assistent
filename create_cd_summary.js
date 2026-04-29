/**
 * create_cd_summary.js
 * Erstellt CD_LRA_Rosenheim_Zusammenfassung.docx
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, BorderStyle, WidthType, ShadingType,
  HeadingLevel, PageNumber, VerticalAlign, LevelFormat
} = require("docx");
const fs = require("fs");
const path = require("path");

// ── Konstanten ─────────────────────────────────────────────────────────────
const OUT = path.join(__dirname, "CD_LRA_Rosenheim_Zusammenfassung.docx");
const H1_COLOR = "1F3864";
const H2_COLOR = "2E75B6";
const HDR_FILL  = "2E75B6";   // Tabellen-Headerzeile
const PAGE_W    = 11906;      // A4-Breite DXA
const MARGIN    = 1440;       // 1 Zoll
const CONT_W    = PAGE_W - 2 * MARGIN; // 9026 DXA Textbreite

// ── Hilfsfunktionen ────────────────────────────────────────────────────────
const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: "Arial", size: 36, bold: true, color: H1_COLOR })],
  spacing: { before: 240, after: 160 },
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: H2_COLOR })],
  spacing: { before: 200, after: 100 },
});

const body = (text, spacingAfter = 120) => new Paragraph({
  children: [new TextRun({ text, font: "Arial", size: 22 })],
  spacing: { after: spacingAfter },
});

const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun({ text, font: "Arial", size: 22 })],
  spacing: { after: 60 },
});

const empty = () => new Paragraph({ children: [new TextRun("")], spacing: { after: 80 } });

const cellBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders    = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };

// Tabellen-Headerzeile
const tblHeader = (cols, widths) => new TableRow({
  tableHeader: true,
  children: cols.map((text, i) => new TableCell({
    borders,
    width: { size: widths[i], type: WidthType.DXA },
    shading: { fill: HDR_FILL, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({ text, font: "Arial", size: 20, bold: true, color: "FFFFFF" })]
    })]
  }))
});

// Normale Tabellenzeile
const tblRow = (cols, widths) => new TableRow({
  children: cols.map((text, i) => new TableCell({
    borders,
    width: { size: widths[i], type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, font: "Arial", size: 20 })]
    })]
  }))
});

const makeTable = (headers, rows, widths) => new Table({
  width: { size: CONT_W, type: WidthType.DXA },
  columnWidths: widths,
  rows: [
    tblHeader(headers, widths),
    ...rows.map(r => tblRow(r, widths))
  ]
});

// ── Dokument ───────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: H1_COLOR },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: H2_COLOR },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: 16838 },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        children: [new TextRun({ text: "LRA Rosenheim – CD-Anpassung Verwaltungs-Assistent", font: "Arial", size: 18, color: "808080" })],
        alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6", space: 4 } }
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        children: [
          new TextRun({ text: "Erstellt: April 2026  |  Projektstudie KI-Assistenzsystem", font: "Arial", size: 16, color: "808080" }),
          new TextRun({ children: ["\t"], font: "Arial" }),
          new TextRun({ text: "Seite ", font: "Arial", size: 16, color: "808080" }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "808080" }),
        ],
        tabStops: [{ type: "right", position: CONT_W }],
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6", space: 4 } }
      })] })
    },
    children: [

      // ── Titel ─────────────────────────────────────────────────────────────
      h1("CD-Anpassung Verwaltungs-Assistent"),
      new Paragraph({
        children: [new TextRun({ text: "Landratsamt Rosenheim – Corporate Design Umsetzung", font: "Arial", size: 24, italics: true, color: "808080" })],
        spacing: { after: 320 },
      }),

      // ── 1. Ziel ────────────────────────────────────────────────────────────
      h2("1. Ziel der Anpassung"),
      body("Der Verwaltungs-Assistent (KI-Assistenzsystem) wurde von einem generischen Design auf das Corporate Design (CD) des Landratsamts Rosenheim umgestellt. Alle exportierten Dokumente (PDF und Word) sowie die Web-Oberfläche entsprechen nun dem visuellen Erscheinungsbild des Landratsamts."),
      body("Kernanforderungen waren:"),
      bullet("LRA-Logo in Kopfzeile aller exportierten Dokumente"),
      bullet("Primärfarbe Orange (#FF6600) und Grau (#808080) durchgängig"),
      bullet("Arial als Hausschrift, vollständige Umlaut-/Sonderzeichen-Unterstützung"),
      bullet("Hinweis \"KI-generierter Entwurf\" sichtbar in allen Ausgabeformaten"),
      bullet("Neuer Word-Export zusätzlich zum bisherigen PDF-Export"),
      empty(),

      // ── 2. Designvorgaben ──────────────────────────────────────────────────
      h2("2. Designvorgaben"),
      makeTable(
        ["Element", "Wert"],
        [
          ["Primärfarbe (Orange)",      "#FF6600  rgb(255, 102, 0)"],
          ["Sekundärfarbe (Grau)",      "#808080  rgb(128, 128, 128)"],
          ["Hintergrund",              "#FFFFFF  Weiß"],
          ["Schriftart",               "Arial (TTF, Windows-Systemschrift)"],
          ["Schriftgröße Fließtext",   "11 pt"],
          ["Schriftgröße Dokumenttitel","16 pt fett"],
          ["Schriftgröße Abschnittsüberschriften","11 pt fett (PDF) / 12 pt fett (Word)"],
          ["Rand links / oben / unten","25 mm"],
          ["Rand rechts",              "20 mm"],
          ["Logo-Pfad",                "backend/assets/lra_logo.jpg  (auch frontend/static/)"],
          ["Logo-Höhe im PDF",         "25 mm (Seite 1) / nicht auf Folgeseiten"],
          ["Logo-Höhe im Word",        "18 mm in Körper-Tabelle oben"],
        ],
        [3600, 5426]
      ),
      empty(),

      // ── 3. Geänderte Dateien ───────────────────────────────────────────────
      h2("3. Geänderte Dateien"),
      makeTable(
        ["Datei", "Art der Änderung"],
        [
          ["backend/pdf_export.py",      "Komplett neu: LRA-Logo, Arial-TTF, Gz./Datum rechts, orange Trennlinien, Titel 16pt fett, KI-Hinweis grau, nummerierte Abschnitte orange, Fußzeile mit Seitenzahl"],
          ["backend/app.py",             "Import docx_export; neuer Endpoint /api/export-docx; PDF-Endpoint nimmt metadata-Objekt entgegen; Dateiname enthält Dokumenttyp + Datum"],
          ["backend/requirements.txt",   "python-docx>=1.1.0 ergänzt"],
          ["requirements.txt (Root)",    "python-docx>=1.1.0 ergänzt"],
          ["frontend/script.js",         "downloadPDF() übergibt jetzt metadata-Objekt; Dateiname mit Typ und Datum"],
          ["README.md",                  "Abschnitt 'Lizenz- und Bildrechte' mit Logo-Hinweis ergänzt"],
        ],
        [3200, 5826]
      ),
      empty(),

      // ── 4. Neue Komponenten ────────────────────────────────────────────────
      h2("4. Neue Komponenten – Word-Export"),
      body("Die neue Datei backend/docx_export.py stellt die Funktion create_docx(text, doc_type, metadata) bereit und liefert die Datei als Bytes zurück. Technologie: python-docx."),
      body("Aufbau des exportierten Word-Dokuments:"),
      bullet("Logo-Header-Tabelle (Logo links, Gz./Datum rechts)  →  orangene Trennlinie"),
      bullet("Dokumenttitel 16 pt fett, zentriert  →  orangene Akzentlinie"),
      bullet("KI-Hinweis-Box (heller Orangehintergrund #FFF4E6, orangene linke Randlinie)"),
      bullet("Metadaten-Block als zweispaltige unsichtbare Tabelle (Label grau, Wert schwarz)"),
      bullet("Fließtext mit nummerierten Abschnittsüberschriften (orange, 12 pt fett)"),
      bullet("Fußzeile: Statustext links  |  Seitenzahl rechts  |  graue Trennlinie oben"),
      bullet("Typografische Anführungszeichen (Smart Quotes, dt. Format „…“)"),
      body("A4-Format, Ränder 25/20/25/25 mm, Schrift Arial 11 pt."),
      empty(),

      // ── 5. PDF-Anpassung ──────────────────────────────────────────────────
      h2("5. PDF-Anpassung"),
      body("Das bisherige PDF (Helvetica, lateinisches Encoding) wurde komplett auf Arial TTF umgestellt. Damit werden alle deutschen Sonderzeichen (Umlaute, §, €) korrekt dargestellt."),
      body("Neue Struktur Seite 1:"),
      bullet("Kopfzeile: LRA-Logo links (25 mm), Gz./Datum rechts (grau 9 pt)"),
      bullet("Orangene Trennlinie (0,5 mm) unterhalb des Logos"),
      bullet("Dokumenttitel 16 pt fett schwarz, zentriert"),
      bullet("Orangene Akzentlinie + grauer KI-Hinweis darunter"),
      bullet("Metadaten-Felder: Schlüssel fett, Wert normal  (10 pt)"),
      bullet("Abschnittsüberschriften: orange, fett 11 pt + dünne orange Unterlinie"),
      bullet("Fließtext: Arial 11 pt, Zeilenabstand 1,4"),
      body("Ab Seite 2: nur \"Landratsamt Rosenheim\" rechtsbündig grau + orange Linie. Fußzeile auf jeder Seite: Statustext grau 8 pt links, Seitenzahl rechts."),
      empty(),

      // ── 6. Web-Oberfläche ──────────────────────────────────────────────────
      h2("6. Web-Oberfläche"),
      body("Die Web-Oberfläche wurde in Sitzung 1 auf das LRA-CD umgestellt. Änderungen im Überblick:"),
      makeTable(
        ["Bereich", "Vorher", "Nachher"],
        [
          ["Header-Logo",      "Zahnrad-Icon (generisch)",        "LRA-Logo (lra_logo.jpg)"],
          ["Primärfarbe",      "Blau #1a3a5c",                    "Orange #FF6600"],
          ["Schriftart",       "System-Schrift / Helvetica",      "Arial"],
          ["Karten",           "Mit Schatten",                    "Ohne Schatten (klarer Verwaltungsstil)"],
          ["Dokumenten-Button","Nur PDF-Button",                  "PDF-Button + Word-Button"],
          ["Briefbogen-Vorschau","Nicht vorhanden",               "Neue .preview-paper-Box mit Titel + Datum"],
        ],
        [2400, 3313, 3313]
      ),
      empty(),

      // ── 7. Logo-Hinweis ────────────────────────────────────────────────────
      h2("7. Logo-Hinweis"),
      new Paragraph({
        children: [new TextRun({
          text: "Das LRA-Logo ist Eigentum des Landratsamts Rosenheim und wird im Prototyp nur zu Demonstrationszwecken im Rahmen der Projektstudie verwendet. Eine kommerzielle Nutzung oder Weitergabe des Logos ist ohne ausdrückliche Genehmigung des Landratsamts Rosenheim nicht gestattet.",
          font: "Arial", size: 22
        })],
        border: {
          left: { style: BorderStyle.SINGLE, size: 12, color: "2E75B6", space: 8 }
        },
        indent: { left: 360 },
        spacing: { after: 160 },
      }),
      body("Der Hinweis ist zusätzlich im README.md des Projekts vermerkt."),
      empty(),

      // ── 8. Test-Ergebnis ───────────────────────────────────────────────────
      h2("8. Test-Ergebnis"),
      makeTable(
        ["Test", "Ergebnis"],
        [
          ["Aktenvermerk – PDF-Export",                    "✅ OK  (86 KB, Logo + oranges CD korrekt)"],
          ["Telefonnotiz – PDF-Export",                    "✅ OK  (85 KB)"],
          ["Besprechungsprotokoll – PDF-Export",           "✅ OK  (85 KB)"],
          ["Aktenvermerk – Word-Export (.docx)",           "✅ OK  (74 KB, Logo-Tabelle, Hint-Box, Metadaten)"],
          ["Telefonnotiz – Word-Export (.docx)",           "✅ OK  (74 KB)"],
          ["Besprechungsprotokoll – Word-Export (.docx)",  "✅ OK  (74 KB)"],
          ["Server-Start (py backend/app.py)",             "✅ Kein Fehler, alle Endpunkte erreichbar"],
          ["Umlaute / Sonderzeichen im PDF",               "✅ Korrekt durch Arial TTF"],
          ["Seitenzahl im PDF (Seite X/Y)",                "✅ Korrekt durch alias_nb_pages()"],
        ],
        [4200, 4826]
      ),
      empty(),

      // ── 9. Bekannte Einschränkungen / Annahmen ─────────────────────────────
      h2("9. Bekannte Einschränkungen / Annahmen"),
      bullet("Arial-Schriftart: Die PDF-Erzeugung setzt Windows mit C:\\Windows\\Fonts\\arial.ttf voraus. Auf Linux/macOS greift der Code automatisch auf Helvetica zurück (Umlaute dann nur latin-1)."),
      bullet("Logo-Pfad: Das Logo muss unter backend/assets/lra_logo.jpg liegen. Fehlt die Datei, wird der Kopfbereich ohne Logo gerendert – kein Absturz."),
      bullet("Word-Seitenzahl: Das PAGE-Feld wird korrekt in .docx geschrieben; Microsoft Word und LibreOffice aktualisieren es beim Öffnen automatisch."),
      bullet("Metadaten-Erkennung: Der Parser erkennt Schlüssel:Wert-Zeilen heuristisch. Sehr lange Schlüsselnamen (>30 Zeichen) oder Zeilen mit Sondersymbolen am Anfang werden als Fließtext behandelt."),
      bullet("python-docx Spaltenbreiten: In manchen docx-Betrachtern weichen die Spaltenbreiten minimal ab, da python-docx keine Gesamt-Tabellenbreite erzwingt. Das Layout ist funktional korrekt."),
      bullet("Dieses Dokument beschreibt den Prototyp-Stand April 2026. Es ist kein Produktivsystem."),
      empty(),
    ]
  }]
});

// ── Ausgabe ────────────────────────────────────────────────────────────────
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("Erstellt: " + OUT);
  console.log("Groesse:  " + buf.length + " Bytes");
});
