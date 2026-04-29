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
    btn.textContent = "KI formuliert... (kann bis zu 30 Sek. dauern)";

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
            updatePreviewPaper(data.doc_type, data.datum);
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
    // Nicht versehentlich bestehende Eingaben überschreiben
    if (formHasUserContent()) {
        if (!confirm("Das Formular enthält bereits Eingaben.\n\nSollen sie durch die Beispieldaten ersetzt werden?")) {
            return;
        }
    }

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
// FORMULAR LEEREN (Reset)
// ============================================================

const FORM_FIELD_IDS = ["datum", "uhrzeit", "beteiligte", "betreff", "notizen", "naechste-schritte"];

function formHasUserContent() {
    return FORM_FIELD_IDS.some(id => {
        const el = document.getElementById(id);
        return el && el.value && el.value.trim() !== "";
    });
}

function resetForm() {
    if (formHasUserContent()) {
        if (!confirm("Alle Eingaben im Formular werden gelöscht.\n\nFortfahren?")) {
            return;
        }
    }

    // Alle Eingabefelder leeren
    FORM_FIELD_IDS.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });

    // Vorlagen-Auswahl zurücksetzen
    const tplSel = document.getElementById("template-select");
    if (tplSel) tplSel.value = "";

    // Fehler- und Output-Bereiche ausblenden
    const errBox = document.getElementById("error-box");
    if (errBox) errBox.style.display = "none";
    const outSec = document.getElementById("output-section");
    if (outSec) outSec.style.display = "none";
    const outText = document.getElementById("output-text");
    if (outText) outText.value = "";

    // Fokus auf das erste Eingabefeld (Bedienkomfort + Barrierefreiheit)
    const docTypeEl = document.getElementById("doc-type");
    if (docTypeEl) docTypeEl.focus();

    showToast("Formular geleert");
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
// LIVE-VORSCHAU (Briefbogen-Kopf) AKTUALISIEREN
// ============================================================

function updatePreviewPaper(docType, datumStr) {
    const titles = {
        aktenvermerk: "AKTENVERMERK",
        telefonnotiz: "TELEFONNOTIZ",
        besprechungsprotokoll: "BESPRECHUNGSPROTOKOLL"
    };
    const titleEl = document.getElementById("preview-paper-title");
    const dateEl = document.getElementById("preview-paper-date");
    if (titleEl) titleEl.textContent = titles[docType] || "DOKUMENT";
    if (dateEl) {
        dateEl.textContent = datumStr || new Date().toLocaleDateString("de-DE");
    }
}


// ============================================================
// PDF HERUNTERLADEN
// ============================================================

async function downloadPDF() {
    const text = document.getElementById("output-text").value;
    const docType = document.getElementById("doc-type").value;
    const btn = document.querySelector(".btn-pdf");

    if (!text.trim()) {
        showErrors(["Kein Dokumenttext vorhanden."]);
        return;
    }

    btn.classList.add("btn-loading");
    const originalText = btn.innerHTML;
    btn.innerHTML = "&#8987; PDF wird erstellt...";

    const metadata = {
        datum:      formatDate(document.getElementById("datum").value),
        uhrzeit:    document.getElementById("uhrzeit").value,
        beteiligte: document.getElementById("beteiligte").value.trim(),
        betreff:    document.getElementById("betreff").value.trim()
    };

    try {
        const response = await fetch("/api/export-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, doc_type: docType, metadata: metadata })
        });

        if (!response.ok) {
            showErrors(["PDF konnte nicht erstellt werden."]);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const titles = { aktenvermerk: "Aktenvermerk", telefonnotiz: "Telefonnotiz", besprechungsprotokoll: "Besprechungsprotokoll" };
        const today  = new Date().toISOString().slice(0, 10);
        a.download = `${titles[docType] || "Dokument"}_${today}.pdf`;
        a.click();
        URL.revokeObjectURL(url);

        btn.innerHTML = "&#10003; PDF heruntergeladen!";
        setTimeout(() => { btn.innerHTML = originalText; }, 2000);
    } catch (error) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
    } finally {
        btn.classList.remove("btn-loading");
    }
}


// ============================================================
// WORD (.docx) HERUNTERLADEN
// ============================================================

async function downloadDOCX() {
    const text = document.getElementById("output-text").value;
    const docType = document.getElementById("doc-type").value;
    const btn = document.getElementById("btn-docx");

    if (!text.trim()) {
        showErrors(["Kein Dokumenttext vorhanden."]);
        return;
    }

    // Metadaten aus dem Formular mitschicken (fuer Header-Block im docx)
    const metadata = {
        datum: formatDate(document.getElementById("datum").value),
        uhrzeit: document.getElementById("uhrzeit").value,
        beteiligte: document.getElementById("beteiligte").value.trim(),
        betreff: document.getElementById("betreff").value.trim()
    };

    btn.classList.add("btn-loading");
    const originalText = btn.innerHTML;
    btn.innerHTML = "&#8987; Word wird erstellt...";

    try {
        const response = await fetch("/api/export-docx", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, doc_type: docType, metadata: metadata })
        });

        if (!response.ok) {
            showErrors(["Word-Dokument konnte nicht erstellt werden."]);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const today = new Date().toISOString().slice(0, 10);
        const titles = { aktenvermerk: "Aktenvermerk", telefonnotiz: "Telefonnotiz", besprechungsprotokoll: "Besprechungsprotokoll" };
        a.download = `${titles[docType] || "Dokument"}_${today}.docx`;
        a.click();
        URL.revokeObjectURL(url);

        btn.innerHTML = "&#10003; Word heruntergeladen!";
        setTimeout(() => { btn.innerHTML = originalText; }, 2000);
    } catch (error) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
    } finally {
        btn.classList.remove("btn-loading");
    }
}


// ============================================================
// SPRACHEINGABE
// ------------------------------------------------------------
// Zwei Pfade:
//  (a) Web Speech API (Chrome/Edge) – läuft komplett im Browser
//      und ist für die Cloud-Workshop-Demo der Standardpfad.
//  (b) MediaRecorder + /api/transcribe (faster-whisper)
//      – Fallback in Browsern ohne Web Speech API oder lokal.
// ============================================================

let mediaRecorder = null;
let audioChunks = [];
let speechRecognition = null;
let speechFinalText = "";
let isRecording = false;
let recordingTimer = null;
let recordingSeconds = 0;
let isPushToTalk = false;

function getSpeechRecognitionCtor() {
    return window.SpeechRecognition || window.webkitSpeechRecognition;
}

async function toggleSpeech() {
    if (isRecording) {
        stopRecording();
    } else if (getSpeechRecognitionCtor()) {
        await startWebSpeechRecording();
    } else {
        await startMediaRecorderRecording();
    }
}

// --- Pfad (a): Web Speech API -------------------------------
async function startWebSpeechRecording() {
    const btn = document.getElementById("btn-speech");
    const SR  = getSpeechRecognitionCtor();
    speechFinalText = "";

    try {
        speechRecognition = new SR();
        speechRecognition.lang = "de-DE";
        speechRecognition.continuous = true;
        speechRecognition.interimResults = true;

        speechRecognition.onresult = (event) => {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    speechFinalText += event.results[i][0].transcript + " ";
                }
            }
        };

        speechRecognition.onerror = (event) => {
            const code = event.error || "unknown";
            if (code === "not-allowed" || code === "permission-denied") {
                showErrors(["Mikrofon-Zugriff nicht erlaubt. Bitte Berechtigung erteilen."]);
            } else if (code === "no-speech") {
                showErrors(["Keine Sprache erkannt. Bitte erneut versuchen."]);
            } else if (code === "network") {
                showErrors(["Kein Internet für die Browser-Spracherkennung. Bitte Verbindung prüfen."]);
            } else if (code !== "aborted") {
                showErrors(["Spracherkennungs-Fehler: " + code]);
            }
        };

        speechRecognition.onend = async () => {
            const text = speechFinalText.trim();
            speechRecognition = null;
            isRecording = false;
            stopTimer();
            btn.classList.remove("recording");

            if (!text) {
                btn.innerHTML = "&#127908; Spracheingabe";
                hideProgress();
                return;
            }

            btn.classList.add("btn-loading");
            btn.innerHTML = "&#8987; Verarbeitung...";
            await processRecognizedText(text);
            btn.classList.remove("btn-loading");
            btn.innerHTML = "&#127908; Spracheingabe";
        };

        speechRecognition.start();
        isRecording = true;
        btn.classList.add("recording");
        startTimer();
        updateRecordingButton();
    } catch (e) {
        showErrors(["Browser-Spracherkennung konnte nicht gestartet werden."]);
        speechRecognition = null;
    }
}

// --- Pfad (b): MediaRecorder + Server-Whisper ---------------
async function startMediaRecorderRecording() {
    const btn = document.getElementById("btn-speech");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            await sendAudioToServer(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        btn.classList.add("recording");
        startTimer();
        updateRecordingButton();
    } catch (error) {
        showErrors(["Mikrofon-Zugriff nicht erlaubt. Bitte Berechtigung erteilen."]);
    }
}

function stopRecording() {
    const btn = document.getElementById("btn-speech");
    if (speechRecognition) {
        // Web Speech: onend kümmert sich um Buttontext und Verarbeitung.
        try { speechRecognition.stop(); } catch (e) {}
        return;
    }
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
    isRecording = false;
    stopTimer();
    btn.classList.remove("recording");
    btn.classList.add("btn-loading");
    btn.innerHTML = "&#8987; Verarbeitung...";
}

// --- Aufnahme-Timer ---
function startTimer() {
    recordingSeconds = 0;
    updateRecordingButton();
    recordingTimer = setInterval(() => {
        recordingSeconds++;
        updateRecordingButton();
    }, 1000);
}

function stopTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    recordingSeconds = 0;
}

function formatTimer(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return m + ":" + s;
}

function updateRecordingButton() {
    const btn = document.getElementById("btn-speech");
    btn.innerHTML = '<span class="rec-dot"></span> ' + formatTimer(recordingSeconds) + ' – Stoppen';
}

// --- Push-to-Talk: Leertaste ---
document.addEventListener("keydown", async (e) => {
    if (e.code !== "Space") return;
    // Nicht auslösen wenn in einem Eingabefeld getippt wird
    const tag = document.activeElement.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

    e.preventDefault();
    if (!isRecording && !isPushToTalk) {
        isPushToTalk = true;
        await startRecording();
    }
});

document.addEventListener("keyup", (e) => {
    if (e.code !== "Space") return;
    const tag = document.activeElement.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

    e.preventDefault();
    if (isRecording && isPushToTalk) {
        isPushToTalk = false;
        stopRecording();
    }
});

// Fortschritt anzeigen
function setStep(stepNum, status) {
    const step = document.getElementById("step-" + stepNum);
    if (!step) return;
    step.className = "progress-step " + status;
    const icon = step.querySelector(".step-icon");
    if (status === "active") icon.textContent = "\u23F3";
    else if (status === "done") icon.textContent = "\u2713";
    else icon.textContent = "\u25CB";
}

function showProgress() {
    document.getElementById("speech-progress").style.display = "block";
    setStep(1, ""); setStep(2, ""); setStep(3, "");
}

function hideProgress() {
    document.getElementById("speech-progress").style.display = "none";
}

// Gemeinsame Nachverarbeitung: Text → Felder extrahieren → Vorschau
async function processRecognizedText(rawText) {
    const speechMode = document.getElementById("speech-mode").value;
    const docType    = document.getElementById("doc-type").value;

    showProgress();
    setStep(1, "done");

    // Einzelfeld-Modus: keine LLM-Extraktion nötig
    if (speechMode !== "formular") {
        setStep(2, "done");
        setStep(3, "active");
        showSingleFieldPreview(rawText, speechMode);
        setStep(3, "done");
        return;
    }

    // Formular-Modus: Felder über /api/extract-fields zerlegen lassen
    setStep(2, "active");
    try {
        const extractRes = await fetch("/api/extract-fields", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ text: rawText, doc_type: docType })
        });
        const extractResult = await extractRes.json();
        setStep(2, "done");

        if (!extractResult.success) {
            // Fallback: alles in Notizen
            showSingleFieldPreview(rawText, "notizen");
            return;
        }

        setStep(3, "active");
        showFieldPreview(rawText, extractResult.fields);
        setStep(3, "done");
    } catch (e) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
        hideProgress();
    }
}

// Fallback-Pfad: Audio-Blob → /api/transcribe (server-side Whisper)
async function sendAudioToServer(audioBlob) {
    const btn = document.getElementById("btn-speech");
    showProgress();
    setStep(1, "active");

    try {
        const formData = new FormData();
        formData.append("audio", audioBlob, "aufnahme.webm");

        const transcribeRes = await fetch("/api/transcribe", {
            method: "POST",
            body:   formData
        });
        const transcribeResult = await transcribeRes.json();

        if (!transcribeResult.success) {
            showErrors(transcribeResult.errors || ["Keine Sprache erkannt."]);
            hideProgress();
            return;
        }

        await processRecognizedText(transcribeResult.text);
    } catch (error) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
        hideProgress();
    } finally {
        btn.classList.remove("btn-loading");
        btn.innerHTML = "&#127908; Spracheingabe";
    }
}

// Vorschau für Einzelfeld-Modus
function showSingleFieldPreview(text, mode) {
    const overlay = document.getElementById("speech-preview-overlay");
    document.getElementById("preview-raw-text").textContent = text;

    // Alle Vorschau-Felder leeren
    document.getElementById("preview-datum").value = "";
    document.getElementById("preview-uhrzeit").value = "";
    document.getElementById("preview-beteiligte").value = "";
    document.getElementById("preview-betreff").value = "";
    document.getElementById("preview-notizen").value = "";
    document.getElementById("preview-schritte").value = "";

    let firstFocusId = "preview-notizen";
    if (mode === "notizen") {
        document.getElementById("preview-notizen").value = text;
        firstFocusId = "preview-notizen";
    } else if (mode === "schritte") {
        document.getElementById("preview-schritte").value = text;
        firstFocusId = "preview-schritte";
    }

    overlay.style.display = "flex";
    overlay.setAttribute("aria-hidden", "false");
    const first = document.getElementById(firstFocusId);
    if (first) first.focus();
}

// Vorschau für ganzes Formular
function showFieldPreview(rawText, fields) {
    const overlay = document.getElementById("speech-preview-overlay");
    document.getElementById("preview-raw-text").textContent = rawText;
    document.getElementById("preview-datum").value = fields.datum || "";
    document.getElementById("preview-uhrzeit").value = fields.uhrzeit || "";
    document.getElementById("preview-beteiligte").value = fields.beteiligte || "";
    document.getElementById("preview-betreff").value = fields.betreff || "";
    document.getElementById("preview-notizen").value = fields.notizen || "";
    document.getElementById("preview-schritte").value = fields.naechste_schritte || "";
    overlay.style.display = "flex";
    overlay.setAttribute("aria-hidden", "false");
    // Fokus für Tastatur-Nutzer:innen auf das erste Eingabefeld setzen
    const first = document.getElementById("preview-datum");
    if (first) first.focus();
}

// Vorschau übernehmen
function applyPreview() {
    const append = document.getElementById("speech-append").checked;

    const fields = {
        datum: document.getElementById("preview-datum").value,
        uhrzeit: document.getElementById("preview-uhrzeit").value,
        beteiligte: document.getElementById("preview-beteiligte").value,
        betreff: document.getElementById("preview-betreff").value,
        notizen: document.getElementById("preview-notizen").value,
        schritte: document.getElementById("preview-schritte").value
    };

    if (fields.datum) document.getElementById("datum").value = parseDate(fields.datum);
    if (fields.uhrzeit) document.getElementById("uhrzeit").value = fields.uhrzeit;

    if (append) {
        appendField("beteiligte", fields.beteiligte);
        appendField("betreff", fields.betreff);
        appendTextarea("notizen", fields.notizen);
        appendTextarea("naechste-schritte", fields.schritte);
    } else {
        if (fields.beteiligte) document.getElementById("beteiligte").value = fields.beteiligte;
        if (fields.betreff) document.getElementById("betreff").value = fields.betreff;
        if (fields.notizen) document.getElementById("notizen").value = fields.notizen;
        if (fields.schritte) document.getElementById("naechste-schritte").value = fields.schritte;
    }

    closePreview();
    document.getElementById("error-box").style.display = "none";
}

function appendField(id, value) {
    if (!value) return;
    const el = document.getElementById(id);
    if (el.value && el.value.trim()) {
        el.value += ", " + value;
    } else {
        el.value = value;
    }
}

function appendTextarea(id, value) {
    if (!value) return;
    const el = document.getElementById(id);
    if (el.value && el.value.trim()) {
        el.value += "\n" + value;
    } else {
        el.value = value;
    }
}

function closePreview() {
    const overlay = document.getElementById("speech-preview-overlay");
    overlay.style.display = "none";
    overlay.setAttribute("aria-hidden", "true");
    hideProgress();
}


// ============================================================
// MODAL: ESC-Taste schließt offenes Overlay,
// Klick auf den dunklen Hintergrund auch
// ============================================================

document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const speechOverlay = document.getElementById("speech-preview-overlay");
    const tplOverlay    = document.getElementById("template-save-overlay");
    if (speechOverlay && speechOverlay.style.display === "flex") {
        closePreview();
    } else if (tplOverlay && tplOverlay.style.display === "flex") {
        closeSaveTemplateModal();
    }
});

// Klick auf den dunklen Hintergrund (nicht in den Modal-Inhalt) schließt
function _wireOverlayBackdropClose(overlayId, closeFn) {
    const overlay = document.getElementById(overlayId);
    if (!overlay) return;
    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeFn();
    });
}
document.addEventListener("DOMContentLoaded", () => {
    _wireOverlayBackdropClose("speech-preview-overlay", closePreview);
    _wireOverlayBackdropClose("template-save-overlay",  closeSaveTemplateModal);
});


// ============================================================
// VORLAGEN
// ============================================================

// Vorlagenliste im Speicher (fuer Ueberschreiben-Check)
let _templateNames = [];

async function loadTemplateList() {
    try {
        const res = await fetch("/api/templates");
        const templates = await res.json();
        _templateNames = templates.map(t => t.name.toLowerCase());
        const select = document.getElementById("template-select");
        const prevValue = select.value;
        select.innerHTML = '<option value="">– Keine Vorlage –</option>';
        templates.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.filename;
            const typeLabel = {
                aktenvermerk: "AV",
                telefonnotiz: "TN",
                besprechungsprotokoll: "BP"
            }[t.doc_type] || "";
            opt.textContent = t.name + (typeLabel ? " (" + typeLabel + ")" : "");
            select.appendChild(opt);
        });
        // Vorherige Auswahl beibehalten falls moeglich
        if (prevValue) select.value = prevValue;
    } catch (e) {
        // Stille Fehlerbehandlung – Vorlagen sind optional
    }
}

async function loadTemplate() {
    const select = document.getElementById("template-select");
    const filename = select.value;
    if (!filename) return;

    try {
        const res = await fetch("/api/templates/" + encodeURIComponent(filename));
        const data = await res.json();
        if (!data.fields) return;

        if (data.doc_type) {
            document.getElementById("doc-type").value = data.doc_type;
        }

        const f = data.fields;
        // Datum auf heute setzen statt altes Datum
        const today = new Date();
        const todayStr = today.getFullYear() + "-"
            + String(today.getMonth() + 1).padStart(2, "0") + "-"
            + String(today.getDate()).padStart(2, "0");
        document.getElementById("datum").value = todayStr;
        document.getElementById("uhrzeit").value = f.uhrzeit || "";
        document.getElementById("beteiligte").value = f.beteiligte || "";
        document.getElementById("betreff").value = f.betreff || "";
        document.getElementById("notizen").value = f.notizen || "";
        document.getElementById("naechste-schritte").value = f.naechste_schritte || "";

        document.getElementById("error-box").style.display = "none";
        showToast("Vorlage geladen – Datum auf heute gesetzt");
    } catch (e) {
        showErrors(["Vorlage konnte nicht geladen werden."]);
    }
}

function openSaveTemplateModal() {
    const input   = document.getElementById("template-name-input");
    const overlay = document.getElementById("template-save-overlay");
    input.value = "";
    input.style.borderColor = "";
    overlay.style.display = "flex";
    overlay.setAttribute("aria-hidden", "false");
    input.focus();
}

function closeSaveTemplateModal() {
    const overlay = document.getElementById("template-save-overlay");
    overlay.style.display = "none";
    overlay.setAttribute("aria-hidden", "true");
}

async function saveTemplate() {
    const input = document.getElementById("template-name-input");
    const name = input.value.trim();
    if (!name) {
        input.style.borderColor = "#c53030";
        return;
    }

    // Ueberschreiben-Warnung
    if (_templateNames.includes(name.toLowerCase())) {
        if (!confirm('Eine Vorlage mit dem Namen "' + name + '" existiert bereits. \u00dcberschreiben?')) {
            return;
        }
    }

    const data = {
        name: name,
        doc_type: document.getElementById("doc-type").value,
        fields: {
            datum: formatDate(document.getElementById("datum").value),
            uhrzeit: document.getElementById("uhrzeit").value,
            beteiligte: document.getElementById("beteiligte").value.trim(),
            betreff: document.getElementById("betreff").value.trim(),
            notizen: document.getElementById("notizen").value.trim(),
            naechste_schritte: document.getElementById("naechste-schritte").value.trim()
        }
    };

    try {
        const res = await fetch("/api/templates", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            closeSaveTemplateModal();
            await loadTemplateList();
            showToast("Vorlage gespeichert!");
        } else {
            showErrors(result.errors || ["Vorlage konnte nicht gespeichert werden."]);
        }
    } catch (e) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
    }
}

async function deleteTemplate() {
    const select = document.getElementById("template-select");
    const filename = select.value;
    if (!filename) return;

    const name = select.options[select.selectedIndex].textContent;
    if (!confirm('Vorlage "' + name + '" wirklich l\u00f6schen?')) return;

    try {
        await fetch("/api/templates/" + encodeURIComponent(filename), { method: "DELETE" });
        await loadTemplateList();
        showToast("Vorlage gel\u00f6scht");
    } catch (e) {
        showErrors(["Vorlage konnte nicht gel\u00f6scht werden."]);
    }
}

async function renameTemplate() {
    const select = document.getElementById("template-select");
    const filename = select.value;
    if (!filename) return;

    const currentName = select.options[select.selectedIndex].textContent.replace(/ \((AV|TN|BP)\)$/, "");
    const newName = prompt("Neuer Name f\u00fcr die Vorlage:", currentName);
    if (!newName || !newName.trim() || newName.trim() === currentName) return;

    try {
        const res = await fetch("/api/templates/" + encodeURIComponent(filename) + "/rename", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_name: newName.trim() })
        });
        const result = await res.json();
        if (result.success) {
            await loadTemplateList();
            // Neue Datei im Dropdown auswaehlen
            if (result.new_filename) {
                document.getElementById("template-select").value = result.new_filename;
            }
            showToast("Vorlage umbenannt!");
        } else {
            showErrors(result.errors || ["Umbenennen fehlgeschlagen."]);
        }
    } catch (e) {
        showErrors(["Verbindung zum Server fehlgeschlagen."]);
    }
}

// Toast-Meldung
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.display = "block";
    toast.classList.remove("toast-hide");
    toast.classList.add("toast-show");
    setTimeout(() => {
        toast.classList.remove("toast-show");
        toast.classList.add("toast-hide");
        setTimeout(() => { toast.style.display = "none"; }, 400);
    }, 2500);
}

// Vorlagen beim Seitenstart laden
document.addEventListener("DOMContentLoaded", loadTemplateList);

// Browser-Hinweis für Spracheingabe nur zeigen, wenn keine Web Speech API verfügbar
document.addEventListener("DOMContentLoaded", () => {
    const hint = document.getElementById("speech-browser-hint");
    if (hint && !getSpeechRecognitionCtor()) {
        hint.style.display = "block";
    }
});


// ============================================================
// COLD-START-ERKENNUNG (Render Free Tier wacht ~50 s)
// ============================================================

(function detectColdStart() {
    const banner = document.getElementById("wake-banner");
    if (!banner) return;

    let countdown = 60;
    let countdownInterval = null;
    let bannerShown = false;

    // Wenn die erste API-Antwort > 1.5 s dauert, gehen wir vom Schlafmodus aus
    const showTimer = setTimeout(() => {
        bannerShown = true;
        banner.style.display = "flex";
        banner.style.opacity = "1";
        const cd = document.getElementById("wake-countdown");
        countdownInterval = setInterval(() => {
            countdown--;
            if (cd) cd.textContent = countdown > 0 ? countdown : "gleich";
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
        }, 1000);
    }, 1500);

    fetch("/api/example?doc_type=aktenvermerk", { cache: "no-store" })
        .catch(() => {})
        .finally(() => {
            clearTimeout(showTimer);
            if (countdownInterval) clearInterval(countdownInterval);
            if (bannerShown) {
                banner.style.opacity = "0";
                setTimeout(() => { banner.style.display = "none"; }, 400);
            }
        });
})();


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
