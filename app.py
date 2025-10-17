# Path: app.py

from flask import Flask, request, render_template
import pandas as pd
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Translations
translations = {
    'en': {
        'Total Time': 'Total Time',
        'Original Interest Without Additional Payments': 'Original Interest Without Additional Payments',
        'Total Interest Paid': 'Total Interest Paid',
        'Total Interest Saved': 'Total Interest Saved',
        'Initial Daily Interest': 'Initial Daily Interest',
        'Final Daily Interest': 'Final Daily Interest',
        'Monthly Payment Details': 'Monthly Payment Details',
        'Month': 'Month',
        'Total Monthly Payment': 'Total Monthly Payment',
        'Interest Payment': 'Interest Payment',
        'Principal Payment': 'Principal Payment',
        'Remaining Principal': 'Remaining Principal',
        'years': 'years',
        'months': 'months',
        'months in total': 'months in total'
    },
    'es': {
        'Total Time': 'Tiempo Total',
        'Original Interest Without Additional Payments': 'Interés Original Sin Pagos Adicionales',
        'Total Interest Paid': 'Total Intereses Pagados',
        'Total Interest Saved': 'Total Intereses Ahorrados',
        'Initial Daily Interest': 'Interés Diario Inicial',
        'Final Daily Interest': 'Interés Diario Final',
        'Monthly Payment Details': 'Detalles de Pagos Mensuales',
        'Month': 'Mes',
        'Total Monthly Payment': 'Pago Mensual Total',
        'Interest Payment': 'Pago Intereses',
        'Principal Payment': 'Pago Principal',
        'Remaining Principal': 'Principal Restante',
        'years': 'años',
        'months': 'meses',
        'months in total': 'meses en total'
    }
}


def calcular_prestamo(principal,
                      tasa_anual,
                      pago_mensual_fijo,
                      pago_mensual_adicional,
                      plazo_anios,
                      plazo_meses,
                      lang='es'):
    """
    Robust amortization:
    - Computes the theoretical base monthly payment from (principal, rate, term).
    - Uses user's fixed monthly payment for the actual schedule if provided; otherwise uses the base.
    - Applies additional monthly payment to principal each period.
    - Blocks negative amortization (payment < monthly interest).
    - Handles 0% interest cleanly.
    - Caps the final payment to avoid negative balances.
    - Returns a clean schedule and summary with correct 'original interest' baseline.
    """

    # ---- Parsing helpers (kept local to avoid global pollution) ----
    def parse_money(value_str: str) -> float:
        return float(value_str.replace('$', '').replace(',', '').strip() or 0)

    def parse_percent(value_str: str) -> float:
        return float(value_str.replace('%', '').strip() or 0)

    # ---- Parse & validate inputs ----
    L = parse_money(principal)
    apr = parse_percent(tasa_anual)
    user_fixed_payment = parse_money(pago_mensual_fijo)
    extra_payment = parse_money(pago_mensual_adicional)
    n = int(plazo_anios) * 12 + int(plazo_meses)

    if L <= 0:
        raise ValueError("Principal must be greater than zero.")
    if n <= 0:
        raise ValueError("Loan term must be at least 1 month.")
    if apr < 0:
        raise ValueError("APR cannot be negative.")
    if extra_payment < 0:
        raise ValueError("Additional payment cannot be negative.")

    r_month = apr / 12.0 / 100.0                 # monthly rate
    r_day = apr / 365.0 / 100.0                  # daily rate (informational)

    # ---- Base (theoretical) amortizing payment for the given term ----
    if abs(r_month) < 1e-12:
        base_payment = L / n
    else:
        base_payment = (r_month * L) / (1.0 - (1.0 + r_month) ** (-n))

    # ---- Actual payment used for the live schedule ----
    # If the user typed a fixed payment, use it. Otherwise, use the base.
    actual_payment = user_fixed_payment if user_fixed_payment > 0 else base_payment
    
    # Are we using the computed base payment with no extras?
    used_base_and_no_extra = (user_fixed_payment <= 1e-9 and extra_payment <= 1e-9)

    # Negative amortization check (only meaningful if r > 0)
    if r_month > 0 and actual_payment <= L * r_month + 1e-9:
        raise ValueError(
            "Monthly payment is too low to cover monthly interest. Increase the payment or extend the term."
        )

    # ---- Baseline 'original interest' (no extras, base_payment) ----
    original_total_paid = base_payment * n
    original_interest = max(original_total_paid - L, 0.0)

    # ---- Build the actual schedule with (actual_payment + extra) ----
    balance = L
    month = 0
    total_interest_paid = 0.0
    schedule_rows = []

    # Safety cap to avoid infinite loops if user tampers inputs
    max_months = n * 2 + 120

    while balance > 1e-8 and month < max_months:
        month += 1
        interest_m = balance * r_month
        payment_total = actual_payment + extra_payment
        
        # If using base payment with no extras, force exact payoff at month n
        if used_base_and_no_extra and month == n:
            principal_m = balance
            payment_total = interest_m + principal_m
            balance = 0.0
            total_interest_paid += interest_m
            schedule_rows.append((
                month,
                f"${payment_total:,.2f}",
                f"${interest_m:,.2f}",
                f"${principal_m:,.2f}",
                f"${balance:,.2f}",
            ))
            break

        # Principal for this month
        principal_m = payment_total - interest_m
        if principal_m <= 0 and r_month > 0:
            # Would increase balance -> reject
            raise ValueError(
                "Payment does not cover interest; the balance would increase. Please raise the monthly payment."
            )

        # Cap the final payment so we never go negative
        if principal_m > balance:
            principal_m = balance
            payment_total = interest_m + principal_m

        balance -= principal_m
        total_interest_paid += interest_m

        schedule_rows.append((
            month,
            f"${payment_total:,.2f}",
            f"${interest_m:,.2f}",
            f"${principal_m:,.2f}",
            f"${max(balance, 0.0):,.2f}",
        ))

        if balance <= 1e-8:
            balance = 0.0
            break

    if month >= max_months and balance > 0:
        raise ValueError("Simulation safety cap reached; check inputs (payment may be too small).")

    interest_savings = max(original_interest - total_interest_paid, 0.0)

    resumen = {
        translations[lang]['Total Time']: f"{month // 12} {translations[lang]['years']}, {month % 12} {translations[lang]['months']} ({month} {translations[lang]['months in total']})",
        translations[lang]['Total Interest Paid']: f"${total_interest_paid:,.2f}",
        translations[lang]['Total Interest Saved']: f"${interest_savings:,.2f}",
        translations[lang]['Initial Daily Interest']: f"${L * r_day:,.2f}",
        translations[lang]['Final Daily Interest']: f"${balance * r_day:,.2f}",
        translations[lang]['Original Interest Without Additional Payments']: f"${original_interest:,.2f}",
    }

    df_pagos = pd.DataFrame(
        schedule_rows,
        columns=[
            translations[lang]['Month'],
            translations[lang]['Total Monthly Payment'],
            translations[lang]['Interest Payment'],
            translations[lang]['Principal Payment'],
            translations[lang]['Remaining Principal'],
        ],
    )

    return df_pagos, resumen


@app.route("/", methods=["GET", "POST"])
def index():
    return handle_request('index.html', 'es')


@app.route("/en", methods=["GET", "POST"])
def index_en():
    return handle_request('index_en.html', 'en')


def handle_request(template, lang):
    form_data = {
        "principal": "",
        "tasa_anual": "",
        "pago_mensual_fijo": "",
        "pago_mensual_adicional": "",
        "plazo_anios": "",
        "plazo_meses": ""
    }

    if request.method == "POST":
        try:
            form_data = {
                "principal": request.form["principal"],
                "tasa_anual": request.form["tasa_anual"],
                "pago_mensual_fijo": request.form["pago_mensual_fijo"],
                "pago_mensual_adicional": request.form["pago_mensual_adicional"],
                "plazo_anios": request.form["plazo_anios"],
                "plazo_meses": request.form["plazo_meses"]
            }

            df_pagos, resumen_final = calcular_prestamo(
                form_data["principal"],
                form_data["tasa_anual"],
                form_data["pago_mensual_fijo"],
                form_data["pago_mensual_adicional"],
                form_data["plazo_anios"],
                form_data["plazo_meses"],
                lang
            )

            # Generate responsive HTML table
            table_html = '<table class="responsive-table">'
            table_html += '<thead><tr>'
            for col in df_pagos.columns:
                table_html += f'<th>{col}</th>'
            table_html += '</tr></thead>'
            table_html += '<tbody>'
            for _, row in df_pagos.iterrows():
                table_html += '<tr>'
                for i, value in enumerate(row):
                    table_html += f'<td data-label="{df_pagos.columns[i]}">{value}</td>'
                table_html += '</tr>'
            table_html += '</tbody></table>'

            return render_template(
                template,
                resumen=resumen_final,
                tables=[table_html],
                form_data=form_data,
                translations=translations[lang]
            )
        except ValueError as e:
            return render_template(
                template,
                error=str(e),
                form_data=form_data,
                translations=translations[lang]
            )
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return render_template(
                template,
                error="An unexpected error occurred. Please try again.",
                form_data=form_data,
                translations=translations[lang]
            )
    return render_template(template, form_data=form_data, translations=translations[lang])


if __name__ == "__main__":
    app.run(debug=True)
