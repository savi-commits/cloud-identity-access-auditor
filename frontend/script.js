/**
 * script.js
 * ---------
 * All interactive logic for the Cloud IAM Auditor dashboard.
 * Talks to the Flask backend at /api/*
 */

"use strict";

// ──────────────────────────────────────────────
// Element references
// ──────────────────────────────────────────────
const btnLoadSample  = document.getElementById("btnLoadSample");
const btnAudit       = document.getElementById("btnAudit");
const btnClear       = document.getElementById("btnClear");
const btnRetry       = document.getElementById("btnRetry");
const fileUpload     = document.getElementById("fileUpload");
const iamInput       = document.getElementById("iamInput");
const errorBox       = document.getElementById("errorBox");
const errorMsg       = document.getElementById("errorMsg");
const resultsSection = document.getElementById("resultsSection");
const statusBadge    = document.getElementById("statusBadge");
const backendBanner  = document.getElementById("backendBanner");

// Summary card value spans
const valUsers    = document.getElementById("val-users");
const valInactive = document.getElementById("val-inactive");
const valExcessive= document.getElementById("val-excessive");
const valRisky    = document.getElementById("val-risky");
const valMfa      = document.getElementById("val-mfa");

// Results elements
const scoreValue   = document.getElementById("scoreValue");
const riskValue    = document.getElementById("riskValue");
const riskBar      = document.getElementById("riskBar");
const findingsBody = document.getElementById("findingsBody");
const noFindings   = document.getElementById("noFindings");
const recsList     = document.getElementById("recsList");
const recsPanel    = document.getElementById("recsPanel");

// Status indicator items
const siSecure = document.getElementById("si-secure");
const siReview = document.getElementById("si-review");
const siHigh   = document.getElementById("si-high");


// ──────────────────────────────────────────────
// Backend health-check
// ──────────────────────────────────────────────

/**
 * Calls GET /api/health.
 * - If reachable: hide the warning banner (or show a brief connected state).
 * - If unreachable: show the warning banner with a Retry button.
 */
async function checkBackendHealth() {
  try {
    const res = await fetch("/api/health", { cache: "no-store" });
    if (res.ok) {
      // Backend is up — hide any warning
      backendBanner.classList.add("hidden");
      backendBanner.classList.remove("connected");
      setBadge("● READY");
    } else {
      showBackendOffline();
    }
  } catch (_) {
    // fetch threw — server is not reachable
    showBackendOffline();
  }
}

function showBackendOffline() {
  backendBanner.classList.remove("hidden", "connected");
  setBadge("● OFFLINE");
}

// Run health-check as soon as the page loads
checkBackendHealth();

// Retry button wires the check again
btnRetry.addEventListener("click", () => {
  btnRetry.textContent = "Checking…";
  btnRetry.disabled = true;
  checkBackendHealth().finally(() => {
    btnRetry.textContent = "↻ Retry Connection";
    btnRetry.disabled = false;
  });
});


// ──────────────────────────────────────────────
// Helper: show / hide error
// ──────────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.classList.add("hidden");
  errorMsg.textContent = "";
}


// ──────────────────────────────────────────────
// Helper: set the status badge text/class
// ──────────────────────────────────────────────
function setBadge(text, scanning = false) {
  statusBadge.textContent = text;
  if (scanning) {
    statusBadge.classList.add("scanning");
  } else {
    statusBadge.classList.remove("scanning");
  }
}


// ──────────────────────────────────────────────
// Button: Load Sample Data
// ──────────────────────────────────────────────
btnLoadSample.addEventListener("click", async () => {
  clearError();
  setBadge("● LOADING…", true);
  btnLoadSample.disabled = true;

  try {
    const response = await fetch("/api/sample-data");
    if (!response.ok) throw new Error(`Server returned ${response.status}`);

    const data = await response.json();
    iamInput.value = JSON.stringify(data, null, 2);
    setBadge("● READY");
  } catch (err) {
    showError("Could not load sample data. Is the Flask server running?");
    setBadge("● ERROR");
  } finally {
    btnLoadSample.disabled = false;
  }
});


// ──────────────────────────────────────────────
// Button: Clear editor
// ──────────────────────────────────────────────
btnClear.addEventListener("click", () => {
  iamInput.value = "";
  clearError();
  resultsSection.classList.add("hidden");
  resetSummaryCards();
  setBadge("● READY");
});


// ──────────────────────────────────────────────
// File upload: read JSON file into textarea
// ──────────────────────────────────────────────
fileUpload.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.name.endsWith(".json")) {
    showError("Please upload a .json file.");
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      // Validate it's valid JSON then pretty-print
      const parsed = JSON.parse(e.target.result);
      iamInput.value = JSON.stringify(parsed, null, 2);
      clearError();
    } catch {
      showError("The uploaded file contains invalid JSON. Please check the format.");
    }
  };
  reader.readAsText(file);

  // Reset the input so the same file can be re-uploaded if needed
  event.target.value = "";
});


// ──────────────────────────────────────────────
// Button: Run Security Audit
// ──────────────────────────────────────────────
btnAudit.addEventListener("click", async () => {
  clearError();

  // 1. Validate textarea is not empty
  const raw = iamInput.value.trim();
  if (!raw) {
    showError("Please load sample data or paste your IAM JSON before running the audit.");
    return;
  }

  // 2. Validate it's valid JSON
  let iamData;
  try {
    iamData = JSON.parse(raw);
  } catch {
    showError("Invalid JSON. Please check for syntax errors (missing quotes, commas, brackets, etc.).");
    return;
  }

  // 3. Send to backend
  setBadge("● SCANNING…", true);
  btnAudit.disabled = true;
  resultsSection.classList.add("hidden");

  try {
    const response = await fetch("/api/audit", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(iamData),
    });

    const result = await response.json();

    if (!response.ok) {
      showError(result.error || "Audit failed. Please check your data format.");
      setBadge("● ERROR");
      return;
    }

    // 4. Render results
    renderResults(result);
    setBadge("● COMPLETE");

  } catch (err) {
    showError("Could not reach the backend. Is the Flask server running on port 5000?");
    setBadge("● ERROR");
  } finally {
    btnAudit.disabled = false;
  }
});


// ──────────────────────────────────────────────
// Render all result sections
// ──────────────────────────────────────────────
function renderResults(data) {
  const { security_score, risk_level, summary, findings, recommendations } = data;

  // ── Summary cards ─────────────────────────
  valUsers.textContent    = summary.total_users    ?? 0;
  valInactive.textContent = summary.inactive_accounts ?? 0;
  valExcessive.textContent= summary.excessive_permissions ?? 0;
  valRisky.textContent    = summary.risky_policies ?? 0;
  valMfa.textContent      = summary.mfa_disabled   ?? 0;

  // ── Security score ─────────────────────────
  scoreValue.textContent = security_score;
  scoreValue.className   = "score-value";  // reset
  if (security_score >= 80)      scoreValue.classList.add("good");
  else if (security_score >= 55) scoreValue.classList.add("medium");
  else                           scoreValue.classList.add("bad");

  // ── Risk level ─────────────────────────────
  riskValue.textContent = risk_level;
  riskValue.className   = `risk-value ${risk_level}`;

  // Risk bar: width % and colour
  const barPercent = security_score;
  riskBar.style.width = barPercent + "%";
  const barColor = {
    LOW:      "#3fb950",
    MEDIUM:   "#d29922",
    HIGH:     "#f85149",
    CRITICAL: "#ff4444",
  }[risk_level] || "#f85149";
  riskBar.style.background = barColor;

  // ── Status indicators ──────────────────────
  siSecure.classList.remove("active");
  siReview.classList.remove("active");
  siHigh.classList.remove("active");

  if (risk_level === "LOW")      siSecure.classList.add("active");
  else if (risk_level === "MEDIUM") siReview.classList.add("active");
  else                           siHigh.classList.add("active");

  // ── Findings table ─────────────────────────
  findingsBody.innerHTML = "";

  if (!findings || findings.length === 0) {
    noFindings.classList.remove("hidden");
    document.querySelector(".table-wrap table").style.display = "none";
  } else {
    noFindings.classList.add("hidden");
    document.querySelector(".table-wrap table").style.display = "";

    findings.forEach((f) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="entity-name">${escHtml(f.entity)}</span></td>
        <td><span class="muted">${escHtml(f.type)}</span></td>
        <td>${escHtml(f.finding)}</td>
        <td><span class="badge badge-${escHtml(f.severity)}">${escHtml(f.severity)}</span></td>
        <td>${escHtml(f.reason)}</td>
        <td>${escHtml(f.recommendation)}</td>
      `;
      findingsBody.appendChild(tr);
    });
  }

  // ── Recommendations ────────────────────────
  recsList.innerHTML = "";
  if (recommendations && recommendations.length > 0) {
    recsPanel.classList.remove("hidden");
    recommendations.forEach((rec) => {
      const li = document.createElement("li");
      li.textContent = rec;
      recsList.appendChild(li);
    });
  } else {
    recsPanel.classList.add("hidden");
  }

  // ── Show results section ───────────────────
  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ──────────────────────────────────────────────
// Reset summary card values to "--"
// ──────────────────────────────────────────────
function resetSummaryCards() {
  [valUsers, valInactive, valExcessive, valRisky, valMfa].forEach(
    (el) => (el.textContent = "--")
  );
}


// ──────────────────────────────────────────────
// Security helper: escape HTML to prevent XSS
// ──────────────────────────────────────────────
function escHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
