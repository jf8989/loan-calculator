// static/scripts.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("loanForm");
  const inputs = form.querySelectorAll('input[type="text"]');
  const resultsContainer = document.getElementById("results");
  const overlay = document.getElementById("loading-overlay");
  const themeBtn = document.getElementById("themeToggle");

  // Ensure each form-group has a persistent error placeholder to avoid reflow
  document.querySelectorAll(".form-group").forEach((group) => {
    let err = group.querySelector(".error-message");
    if (!err) {
      err = document.createElement("span");
      err.className = "error-message";
      err.setAttribute("aria-live", "polite");
      group.appendChild(err);
    }
  });

  // --- Theme setup (persist to localStorage) ---
  initTheme(themeBtn);

  // --- If results are visible after a POST, auto-scroll to them ---
  setTimeout(() => {
    if (resultsContainer && !resultsContainer.classList.contains("hidden")) {
      resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, 150);

  // --- Show overlay spinner during submit (classic POST) ---
  form.addEventListener("submit", function (event) {
    let isValid = true;

    inputs.forEach((input) => {
      if (input.value.trim() === "") {
        isValid = false;
        showError(input, getRequiredMessage());
      } else {
        hideError(input);
      }
    });

    if (!isValid) {
      event.preventDefault();
      return;
    }

    if (overlay) {
      overlay.classList.add("active");
      overlay.setAttribute("aria-hidden", "false");
      form.querySelector(".btn-calculate")?.setAttribute("disabled", "true");
    }
  });

  // Input field event listeners
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("focused");
    });

    input.addEventListener("blur", function () {
      this.parentElement.classList.remove("focused");
      if (this.value.trim() === "") {
        showError(this, getRequiredMessage());
      } else {
        hideError(this);
      }
    });

    input.addEventListener("input", function () {
      hideError(this);
    });
  });

  // Currency formatting
  const currencyInputs = ["principal", "pago_mensual_fijo", "pago_mensual_adicional"];
  currencyInputs.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("blur", function () {
      formatCurrency(this);
    });
  });

  // Percentage formatting
  const aprInput = document.getElementById("tasa_anual");
  if (aprInput) {
    aprInput.addEventListener("blur", function () {
      formatPercentage(this);
    });
  }

  // Plazo input validation (numbers only)
  ["plazo_anios", "plazo_meses"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "");
    });
  });

  // Masks for better UX (kept)
  setupInputMasks();

  // Close modal on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLegal();
  });
});

/* ------------------ Theming ------------------ */
function initTheme(themeBtn) {
  const stored = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = stored || (prefersDark ? "dark" : "light");
  setTheme(theme);

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const next = document.body.classList.contains("theme-dark") ? "light" : "dark";
      setTheme(next);
    });
  }

  function setTheme(t) {
    document.body.classList.toggle("theme-dark", t === "dark");
    localStorage.setItem("theme", t);
    if (themeBtn) {
      themeBtn.innerHTML = t === "dark" ? '<i class="fas fa-sun"></i> Light' : '<i class="fas fa-moon"></i> Dark';
      themeBtn.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
    }
  }
}

/* ------------------ Reset & formatting helpers (existing, kept) ------------------ */
function resetForm() {
  const form = document.getElementById("loanForm");
  form.reset();
  clearResults();

  const inputs = form.querySelectorAll('input[type="text"]');
  inputs.forEach((input) => {
    hideError(input);
    input.style.transition = "background-color 0.3s ease";
    input.style.backgroundColor = "#fff9c4";
    setTimeout(() => {
      input.style.backgroundColor = "white";
    }, 300);
  });
}

function clearResults() {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";
  resultsDiv.classList.add("hidden");
}

function formatCurrency(input) {
  let value = input.value.replace(/[^\d.]/g, "");
  let parts = value.split(".");
  if (parts.length > 2) {
    parts = [parts[0], parts.slice(1).join("")];
  }
  value = parts.join(".");
  let numValue = parseFloat(value);
  if (!isNaN(numValue)) {
    const formatted = "$" + numValue.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    input.value = formatted;
  } else {
    input.value = "";
  }
}

function formatPercentage(input) {
  let raw = input.value.replace(/[^\d.]/g, "");
  if (raw === "") {
    input.value = "";
    return;
  }
  const parts = raw.split(".");
  if (parts.length > 2) raw = parts[0] + "." + parts.slice(1).join("");
  let value = parseFloat(raw);
  if (isNaN(value)) { input.value = ""; return; }
  value = Math.round(value * 100) / 100;
  input.value = value.toFixed(2) + "%";
}

function showError(input, message) {
  input.classList.add("error");
  const errorElement = input.parentElement.querySelector(".error-message");
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = "block";
  }
}

function hideError(input) {
  input.classList.remove("error");
  const errorElement = input.parentElement.querySelector(".error-message");
  if (errorElement) {
    errorElement.textContent = "";
    errorElement.style.display = "none";
  }
}

function updateSummaryText(principal, tasaAnual, pagoMensualFijo, pagoMensualAdicional) {
  const summaryText = document.getElementById("summary-text");
  if (!summaryText) return;
  const currentDate = new Date().toLocaleDateString("es-ES");
  summaryText.textContent =
    `Para pagar un préstamo cuyo principal a la fecha actual, ${currentDate}, ` +
    `con una tasa de interés del ${tasaAnual}% anual, pagando de manera fija ` +
    `$${pagoMensualFijo} al mes y aplicando un pago adicional mensual de ` +
    `$${pagoMensualAdicional}:`;
}

// Smooth scroll helper (kept)
function scrollToResults() {
  const resultsElement = document.getElementById("results");
  if (resultsElement) {
    resultsElement.scrollIntoView({ behavior: "smooth" });
  }
}

// Input masks (kept, with safety tweaks)
function setupInputMasks() {
  const currencyIds = ["principal", "pago_mensual_fijo", "pago_mensual_adicional"];
  currencyIds.forEach((id) => {
    const input = document.getElementById(id);
    if (!input) return;

    input.addEventListener("input", function (e) {
      let value = e.target.value.replace(/[^\d.]/g, "");
      const decimalIndex = value.indexOf(".");
      if (decimalIndex !== -1) {
        const integerPart = value.slice(0, decimalIndex);
        let decimalPart = value.slice(decimalIndex + 1);
        decimalPart = decimalPart.slice(0, 2);
        value = integerPart + "." + decimalPart;
      }
      const parts = value.split(".");
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      e.target.value = (parts.join(".") ? "$" : "") + parts.join(".");
    });

    input.addEventListener("blur", function () {
      if (!input.value) return;
      const numValue = parseFloat(input.value.replace(/[^\d.]/g, ""));
      if (!isNaN(numValue)) {
        input.value = "$" + numValue.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      }
    });
  });

  const percentInput = document.getElementById("tasa_anual");
  if (percentInput) {
    percentInput.addEventListener("input", function (e) {
      let value = e.target.value.replace(/[^\d.]/g, "");
      if (!value) { e.target.value = ""; return; }
      const parts = value.split(".");
      if (parts[1] && parts[1].length > 2) parts[1] = parts[1].slice(0, 2);
      value = parts.join(".");
      e.target.value = value + "%";
    });
  }
}

function getRequiredMessage() {
  const lang = document.documentElement.lang || "en";
  return lang.startsWith("es") ? "Este campo es requerido" : "This field is required";
}

/* ------------------ PDF download (reliable: browser print) ------------------ */
function downloadReportPDF() {
  const results = document.getElementById("results");
  if (!results || results.classList.contains("hidden")) {
    const lang = document.documentElement.lang || "en";
    alert(lang.startsWith("es")
      ? "Primero calcula el préstamo para generar el reporte."
      : "Please calculate the loan first to generate the report.");
    return;
  }
  const wasDark = document.body.classList.contains("theme-dark");
  if (wasDark) document.body.classList.remove("theme-dark");
  window.print();
  if (wasDark) setTimeout(() => document.body.classList.add("theme-dark"), 50);
}
window.downloadReportPDF = downloadReportPDF;

/* ------------------ Legal modal ------------------ */
function openLegal() {
  const modal = document.getElementById("legal-modal");
  const backdrop = document.getElementById("modal-backdrop");
  if (!modal || !backdrop) return;
  modal.classList.add("show");
  backdrop.classList.add("show");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  // focus trap start
  const closeBtn = modal.querySelector(".modal-close");
  if (closeBtn) closeBtn.focus();
}

function closeLegal() {
  const modal = document.getElementById("legal-modal");
  const backdrop = document.getElementById("modal-backdrop");
  if (!modal || !backdrop) return;
  modal.classList.remove("show");
  backdrop.classList.remove("show");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}
window.openLegal = openLegal;
window.closeLegal = closeLegal;
