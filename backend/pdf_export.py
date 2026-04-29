"""
pdf_export.py – PDF-Generierung im LRA Rosenheim Corporate Design
"""
import io
import os
from datetime import date
from fpdf import FPDF

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "lra_logo.jpg")
ORANGE    = (255, 102,   0)
GREY      = (128, 128, 128)
BLACK     = ( 30,  30,  30)

# Plattformneutrale Schrift-Suche
# 1. Windows-Arial  2. Linux-DejaVu (Render/Ubuntu)  3. macOS  4. Helvetica-Fallback
FONT_CANDIDATES = [
    ("Arial",
     r"C:\Windows\Fonts\arial.ttf",
     r"C:\Windows\Fonts\arialbd.ttf"),
    ("DejaVu",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("DejaVu",
     "/usr/share/fonts/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ("Arial",
     "/Library/Fonts/Arial.ttf",
     "/Library/Fonts/Arial Bold.ttf"),
]

DOC_TYPE_LABELS = {
    "aktenvermerk":          "AKTENVERMERK",
    "telefonnotiz":          "TELEFONNOTIZ",
    "besprechungsprotokoll": "BESPRECHUNGSPROTOKOLL",
}
DOC_FILENAMES = {
    "aktenvermerk":          "Aktenvermerk",
    "telefonnotiz":          "Telefonnotiz",
    "besprechungsprotokoll": "Besprechungsprotokoll",
}


class LraPDF(FPDF):
    def __init__(self, doc_type="", datum=""):
        super().__init__()
        self.doc_type  = doc_type
        self.doc_label = DOC_TYPE_LABELS.get(doc_type, "DOKUMENT")
        self.datum     = datum
        self.set_margins(left=25, top=10, right=20)
        self._fn = self._load_unicode_font()

    def _load_unicode_font(self):
        """Sucht eine Unicode-fähige Schrift; fällt auf Helvetica zurück.
        Helvetica unterstützt Latin-1, aber viele typografische Sonderzeichen
        (€, „", §, …) werden dort als ? dargestellt."""
        for name, regular, bold in FONT_CANDIDATES:
            if os.path.isfile(regular) and os.path.isfile(bold):
                try:
                    self.add_font(name, "",  regular)
                    self.add_font(name, "B", bold)
                    return name
                except Exception:
                    continue
        return "Helvetica"

    def _orange_line(self, y=None):
        if y is None:
            y = self.get_y()
        self.set_draw_color(*ORANGE)
        self.set_line_width(0.5)
        self.line(self.l_margin, y, self.w - self.r_margin, y)

    def _grey_line(self, y=None):
        if y is None:
            y = self.get_y()
        self.set_draw_color(*GREY)
        self.set_line_width(0.3)
        self.line(self.l_margin, y, self.w - self.r_margin, y)

    def header(self):
        if self.page_no() == 1:
            if os.path.exists(LOGO_PATH):
                self.image(LOGO_PATH, x=self.l_margin, y=10, h=25)
            self.set_font(self._fn, "", 9)
            self.set_text_color(*GREY)
            self.set_xy(self.l_margin, 12)
            self.cell(0, 5, "Gz.: ____", align="R")
            self.set_xy(self.l_margin, 18)
            self.cell(0, 5, self.datum or date.today().strftime("%d.%m.%Y"), align="R")
            self._orange_line(y=38)
            self.set_y(43)
        else:
            self.set_font(self._fn, "", 9)
            self.set_text_color(*GREY)
            self.set_xy(self.l_margin, 10)
            self.cell(0, 6, "Landratsamt Rosenheim", align="R")
            self._orange_line(y=19)
            self.set_y(23)

    def footer(self):
        self.set_y(-22)
        y = self.get_y()
        self._grey_line(y)
        self.set_y(y + 2)
        self.set_font(self._fn, "", 8)
        self.set_text_color(*GREY)
        avail = self.w - self.l_margin - self.r_margin
        self.set_x(self.l_margin)
        self.cell(
            avail * 0.70, 5,
            "Dokumentenstatus: Entwurf | KI-generiert – vor Ablage fachlich prüfen",
            align="L"
        )
        self.cell(avail * 0.30, 5, f"Seite {self.page_no()}/{{nb}}", align="R")


def create_pdf(text: str, doc_type: str = "", metadata: dict = None) -> bytes:
    if metadata is None:
        metadata = {}
    datum = metadata.get("datum", "")

    pdf = LraPDF(doc_type, datum)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    title_drawn = False
    for line in text.split("\n"):
        s = line.strip()

        if not s:
            pdf.ln(3)
            continue

        if len(s) > 2 and all(c in "=-" for c in s):
            continue

        # Erster ALL-CAPS-Block = Dokumenttitel
        if not title_drawn and s.upper() == s and len(s) >= 3 and not s[0].isdigit():
            title_drawn = True
            pdf.set_font(pdf._fn, "B", 16)
            pdf.set_text_color(*BLACK)
            pdf.ln(2)
            pdf.set_x(pdf.l_margin)
            pdf.cell(0, 10, s, align="C")
            pdf.ln(10)
            pdf._orange_line()
            pdf.ln(4)
            pdf.set_font(pdf._fn, "", 9)
            pdf.set_text_color(*GREY)
            pdf.set_x(pdf.l_margin)
            pdf.cell(
                0, 5,
                "KI-generierter Entwurf – vor Ablage fachlich prüfen",
                align="C"
            )
            pdf.ln(8)
            continue

        # Nummerierte Abschnittsüberschriften (z. B. "1. ANLASS UND SACHVERHALT")
        if s[0].isdigit() and len(s) > 2 and s[1] in (".", " "):
            rest = s.split(".", 1)[-1].strip() if "." in s[:3] else s
            if rest.isupper():
                pdf.ln(4)
                pdf.set_font(pdf._fn, "B", 11)
                pdf.set_text_color(*ORANGE)
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 7, s)
                pdf.ln(7)
                pdf.set_draw_color(*ORANGE)
                pdf.set_line_width(0.3)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                pdf.ln(4)
                continue

        # Metadaten-Felder (Schlüssel: Wert)
        if ":" in s and not s[0].isdigit():
            colon = s.index(":")
            key   = s[:colon].strip()
            val   = s[colon + 1:].strip()
            clean = key.replace(" ", "").replace("/", "").replace("-", "")
            if len(key) < 30 and clean.isalpha():
                pdf.set_font(pdf._fn, "B", 10)
                pdf.set_text_color(50, 50, 50)
                pdf.set_x(pdf.l_margin)
                kw = pdf.get_string_width(key + ": ") + 2
                pdf.cell(kw, 6, key + ":")
                pdf.set_font(pdf._fn, "", 10)
                pdf.set_text_color(*BLACK)
                pdf.cell(0, 6, val)
                pdf.ln(6)
                continue

        # Fließtext 11 pt, Zeilenabstand ~1.4
        pdf.set_font(pdf._fn, "", 11)
        pdf.set_text_color(*BLACK)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5.5, s)
        pdf.ln(1)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
