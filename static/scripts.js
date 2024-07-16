document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("loanForm");
  const inputs = form.querySelectorAll('input[type="text"]');
  const resultsContainer = document.getElementById("results");

  // Form submission handler
  form.addEventListener("submit", function (event) {
    let isValid = true;

    inputs.forEach((input) => {
      if (input.value.trim() === "") {
        isValid = false;
        showError(input, "Este campo es requerido");
      } else {
        hideError(input);
      }
    });

    if (!isValid) {
      event.preventDefault();
    } else {
      // Animate results container
      resultsContainer.style.opacity = "0";
      setTimeout(() => {
        resultsContainer.style.opacity = "1";
      }, 300);
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
        showError(this, "Este campo es requerido");
      } else {
        hideError(this);
      }
    });

    input.addEventListener("input", function () {
      hideError(this);
    });
  });

  // Currency formatting
  const currencyInputs = [
    "principal",
    "pago_mensual_fijo",
    "pago_mensual_adicional",
  ];
  currencyInputs.forEach((id) => {
    document.getElementById(id).addEventListener("blur", function () {
      formatCurrency(this);
    });
  });

  // Percentage formatting
  document.getElementById("tasa_anual").addEventListener("blur", function () {
    formatPercentage(this);
  });

  // Plazo input validation
  const plazoInputs = ["plazo_anios", "plazo_meses"];
  plazoInputs.forEach((id) => {
    document.getElementById(id).addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "");
    });
  });
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
    }, 500);
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
    const formatter = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    input.value = formatter.format(numValue);
  } else {
    input.value = "";
  }
}

function formatPercentage(input) {
  let value = parseFloat(input.value.replace(/[^\d.]/g, ""));
  if (!isNaN(value)) {
    input.value = value.toFixed(2) + "%";
  }
}

function showError(input, message) {
  input.classList.add("error");
  const errorElement = input.parentElement.querySelector(".error-message");
  if (errorElement) {
    errorElement.textContent = message;
  } else {
    const newErrorElement = document.createElement("span");
    newErrorElement.className = "error-message";
    newErrorElement.textContent = message;
    input.parentElement.appendChild(newErrorElement);
  }
}

function hideError(input) {
  input.classList.remove("error");
  const errorElement = input.parentElement.querySelector(".error-message");
  if (errorElement) {
    errorElement.remove();
  }
}

function updateSummaryText(
  principal,
  tasaAnual,
  pagoMensualFijo,
  pagoMensualAdicional
) {
  const summaryText = document.getElementById("summary-text");
  const currentDate = new Date().toLocaleDateString("es-ES");
  summaryText.textContent = `Para pagar un préstamo cuyo principal a la fecha actual, ${currentDate}, con una tasa de interés del ${tasaAnual}% anual, pagando de manera fija $${pagoMensualFijo} al mes y aplicando un pago adicional mensual de $${pagoMensualAdicional}:`;
}

// Add smooth scrolling to results
function scrollToResults() {
  const resultsElement = document.getElementById("results");
  if (resultsElement) {
    resultsElement.scrollIntoView({ behavior: "smooth" });
  }
}

// Add input masking for better user experience
function setupInputMasks() {
  const currencyInputs = [
    "principal",
    "pago_mensual_fijo",
    "pago_mensual_adicional",
  ];
  currencyInputs.forEach((id) => {
    const input = document.getElementById(id);
    input.addEventListener("input", function (e) {
      let value = e.target.value.replace(/[^\d.]/g, "");

      // Allow only one decimal point
      const decimalIndex = value.indexOf(".");
      if (decimalIndex !== -1) {
        const integerPart = value.slice(0, decimalIndex);
        let decimalPart = value.slice(decimalIndex + 1);
        // Limit decimal part to two digits
        decimalPart = decimalPart.slice(0, 2);
        value = integerPart + "." + decimalPart;
      }

      // Format the number
      const parts = value.split(".");
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");

      e.target.value = "$" + parts.join(".");
    });

    // Ensure correct formatting on blur
    input.addEventListener("blur", function () {
      if (input.value) {
        const numValue = parseFloat(input.value.replace(/[^\d.]/g, ""));
        if (!isNaN(numValue)) {
          input.value =
            "$" + numValue.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
      }
    });
  });

  const percentInput = document.getElementById("tasa_anual");
  percentInput.addEventListener("input", function (e) {
    let value = e.target.value.replace(/[^\d.]/g, "");
    if (value) {
      const parts = value.split(".");
      if (parts[0].length > 2) {
        parts[0] = parts[0].slice(0, 2);
      }
      if (parts[1] && parts[1].length > 2) {
        parts[1] = parts[1].slice(0, 2);
      }
      value = parts.join(".");
      e.target.value = value + "%";
    }
  });
}

// Call setup functions
setupInputMasks();
