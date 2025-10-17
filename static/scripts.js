// static/scripts.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("loanForm");
  const inputs = form.querySelectorAll('input[type="text"]');
  const resultsContainer = document.getElementById("results");

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

  // Form submission handler (simple client validation)
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

    // Fade results container for a nicer transition without layout jump
    if (resultsContainer) {
      resultsContainer.style.opacity = "0";
      setTimeout(() => {
        resultsContainer.style.opacity = "1";
      }, 200);
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
});

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
  // Remove non-digit characters except for the decimal point
  let value = input.value.replace(/[^\d.]/g, "");

  // Ensure only one decimal point
  let parts = value.split(".");
  if (parts.length > 2) {
    parts = [parts[0], parts.slice(1).join("")];
  }
  value = parts.join(".");

  // Parse the value and format it
  let numValue = parseFloat(value);
  if (!isNaN(numValue)) {
    const formatted =
      "$" + numValue.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
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
  if (parts.length > 2) {
    raw = parts[0] + "." + parts.slice(1).join("");
  }
  let value = parseFloat(raw);
  if (isNaN(value)) {
    input.value = "";
    return;
  }
  // Cap to two decimals
  value = Math.round(value * 100) / 100;
  input.value = value.toFixed(2) + "%";
}

function showError(input, message) {
  input.classList.add("error");
  const errorElement = input.parentElement.querySelector(".error-message");
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = "block"; // don’t insert/remove → no layout jump
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

// Smooth scroll helper (unused here; kept for future)
function scrollToResults() {
  const resultsElement = document.getElementById("results");
  if (resultsElement) {
    resultsElement.scrollIntoView({ behavior: "smooth" });
  }
}

// Input masks (kept, but with small safety tweaks)
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
  // Simple bilingual fallback based on page lang
  const lang = document.documentElement.lang || "en";
  return lang.startsWith("es") ? "Este campo es requerido" : "This field is required";
}
