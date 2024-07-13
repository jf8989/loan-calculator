document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loanForm');
    const inputs = form.querySelectorAll('input[type="text"]');
    const resultsContainer = document.getElementById('results');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 0 2px rgba(52, 152, 219, 0.5)';
        });

        input.addEventListener('blur', function() {
            this.style.boxShadow = 'none';
        });
    });

    form.addEventListener('submit', function() {
        resultsContainer.style.opacity = '0';
        setTimeout(() => {
            resultsContainer.style.opacity = '1';
        }, 300);
    });
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
    });
}

function clearResults() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    resultsDiv.style.display = 'none';
}

// Add this function to format currency inputs
function formatCurrency(input) {
    let value = input.value.replace(/[^\d]/g, '');
    value = (parseInt(value, 10) / 100).toFixed(2);
    input.value = '$' + value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Add event listeners for currency formatting
document.getElementById('principal').addEventListener('blur', function() { formatCurrency(this); });
document.getElementById('pago_mensual_fijo').addEventListener('blur', function() { formatCurrency(this); });
document.getElementById('pago_mensual_adicional').addEventListener('blur', function() { formatCurrency(this); });