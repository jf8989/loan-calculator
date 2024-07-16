document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loanForm');
    const inputs = form.querySelectorAll('input[type="text"]');
    const resultsContainer = document.getElementById('results');

    form.addEventListener('submit', function(event) {
        const inputs = form.querySelectorAll('input[type="text"]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (input.value.trim() === '') {
                isValid = false;
                input.style.borderColor = 'red';
            } else {
                input.style.borderColor = '';
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            alert('Por favor, complete todos los campos');
        } else {
            resultsContainer.style.opacity = '0';
            setTimeout(() => {
                resultsContainer.style.opacity = '1';
            }, 300);
        }
    });

    form.addEventListener('focusin', function(event) {
        if (event.target.tagName === 'INPUT') {
            event.target.style.boxShadow = '0 0 0 2px rgba(52, 152, 219, 0.5)';
        }
    });

    form.addEventListener('focusout', function(event) {
        if (event.target.tagName === 'INPUT') {
            event.target.style.boxShadow = 'none';
        }
    });

    // Add event listeners for currency formatting
    document.getElementById('principal').addEventListener('blur', function() { formatCurrency(this); });
    document.getElementById('pago_mensual_fijo').addEventListener('blur', function() { formatCurrency(this); });
    document.getElementById('pago_mensual_adicional').addEventListener('blur', function() { formatCurrency(this); });
});

function resetForm() {
    const form = document.getElementById('loanForm');
    form.reset();
    clearResults();
    
    // Add animation to form fields
    const inputs = form.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.style.transition = 'background-color 0.3s ease';
        input.style.backgroundColor = '#fff9c4';
        setTimeout(() => {
            input.style.backgroundColor = 'white';
        }, 500);
        input.style.borderColor = ''; // Reset border color
    });
}

function clearResults() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    resultsDiv.style.display = 'none';
}

function formatCurrency(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    });
    input.value = formatter.format(value);
}

// Function to update summary text
function updateSummaryText(principal, tasaAnual, pagoMensualFijo, pagoMensualAdicional) {
    const summaryText = document.getElementById('summary-text');
    const currentDate = new Date().toLocaleDateString('es-ES');
    summaryText.textContent = `Para pagar un préstamo cuyo principal a la fecha actual, ${currentDate}, con una tasa de interés del ${tasaAnual}% anual, pagando de manera fija $${pagoMensualFijo} al mes y aplicando un pago adicional mensual de $${pagoMensualAdicional}:`;
}