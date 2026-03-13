/**
 * script.js – Frontend-Logik für das KI-Assistenzsystem
 *
 * Funktionen:
 * - generateDocument()  → Entwurf über die API erstellen
 * - loadExample()       → Beispieldaten einfügen
 * - copyText()          → Ausgabetext in die Zwischenablage kopieren
 */

// ============================================================
// DOKUMENT GENERIEREN
// ============================================================

async function generateDocument() {
    const btn = document.getElementById("btn-generate");
    const errorBox = document.getElementById("error-box");
    const outputSection = document.getElementById("output-section");

    // Fehlerbox zurücksetzen
    errorBox.style.display = "none";

    // Formulardaten sammeln
    const data = {
        doc_type: document.getElementById("doc-type").value,
        datum: formatDate(document.getElementById("datum").value),
        uhrzeit: document.getElementById("uhrzeit").value,
        beteiligte: document.getElementById("beteiligte").value.trim(),
        betreff: document.getElementById("betreff").value.trim(),
        notizen: document.getElementById("notizen").value.trim(),
        naechste_schritte: document.getElementById("naechste-schritte").value.trim()
    };

    // Button deaktivieren während der Verarbeitung
    btn.classList.add("btn-loading");
    btn.textContent = "Wird erstellt...";

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            // Ausgabe anzeigen
            document.getElementById("output-text").value = result.text;
            outputSection.style.display = "block";
            outputSection.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
            // Fehlermeldungen anzeigen
            showErrors(result.errors);
        }
    } catch (error) {
        showErrors(["Verbindung zum Server fehlgeschlagen. Läuft der Server?"]);
    } finally {
        // Button wiederherstellen
        btn.classList.remove("btn-loading");
        btn.textContent = "Entwurf erstellen";
    }
}


// ============================================================
// BEISPIELDATEN LADEN
// ============================================================

async function loadExample() {
    const docType = document.getElementById("doc-type").value;

    try {
        const response = await fetch(`/api/example?doc_type=${docType}`);
        const data = await response.json();

        // Felder befüllen
        document.getElementById("datum").value = parseDate(data.datum);
        document.getElementById("uhrzeit").value = data.uhrzeit || "";
        document.getElementById("beteiligte").value = data.beteiligte || "";
        document.getElementById("betreff").value = data.betreff || "";
        document.getElementById("notizen").value = data.notizen || "";
        document.getElementById("naechste-schritte").value = data.naechste_schritte || "";

        // Fehlerbox ausblenden
        document.getElementById("error-box").style.display = "none";
    } catch (error) {
        showErrors(["Beispieldaten konnten nicht geladen werden."]);
    }
}


// ============================================================
// TEXT KOPIEREN
// ============================================================

async function copyText() {
    const text = document.getElementById("output-text").value;
    const btn = document.querySelector(".btn-copy");

    try {
        await navigator.clipboard.writeText(text);

        // Visuelles Feedback
        const originalText = btn.innerHTML;
        btn.innerHTML = "&#10003; Kopiert!";
        btn.classList.add("copy-success");

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove("copy-success");
        }, 2000);
    } catch (error) {
        // Fallback für ältere Browser
        document.getElementById("output-text").select();
        document.execCommand("copy");
    }
}


// ============================================================
// HILFSFUNKTIONEN
// ============================================================

/**
 * Deutsches Datum (DD.MM.YYYY) aus HTML-Date-Input (YYYY-MM-DD) erzeugen.
 */
function formatDate(isoDate) {
    if (!isoDate) return "";
    const parts = isoDate.split("-");
    return `${parts[2]}.${parts[1]}.${parts[0]}`;
}

/**
 * Deutsches Datum (DD.MM.YYYY) in HTML-Date-Format (YYYY-MM-DD) umwandeln.
 */
function parseDate(germanDate) {
    if (!germanDate) return "";
    const parts = germanDate.split(".");
    if (parts.length !== 3) return "";
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
}

/**
 * Fehlermeldungen anzeigen.
 */
function showErrors(errors) {
    const errorBox = document.getElementById("error-box");
    if (errors.length === 1) {
        errorBox.innerHTML = errors[0];
    } else {
        errorBox.innerHTML = "<ul>" + errors.map(e => `<li>${e}</li>`).join("") + "</ul>";
    }
    errorBox.style.display = "block";
    errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
}
