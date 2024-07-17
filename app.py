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

def calcular_prestamo(principal, tasa_anual, pago_mensual_fijo, pago_mensual_adicional, plazo_anios, plazo_meses, lang='es'):
    try:
        # Convert inputs to appropriate types
        principal = float(principal.replace('$', '').replace(',', ''))
        tasa_anual = float(tasa_anual.replace('%', ''))
        pago_mensual_fijo = float(pago_mensual_fijo.replace('$', '').replace(',', ''))
        pago_mensual_adicional = float(pago_mensual_adicional.replace('$', '').replace(',', ''))
        plazo_total_meses = int(plazo_anios) * 12 + int(plazo_meses)

        # Calculate monthly interest rate
        tasa_mensual = tasa_anual / 12 / 100

        # Calculate daily interest rate
        tasa_diaria = tasa_anual / 365 / 100

        # Calculate original interest if no additional payments are made
        total_pagos_original = pago_mensual_fijo * plazo_total_meses
        interes_original = total_pagos_original - principal

        pagos = []
        total_intereses_pagados = 0
        mes = 0
        saldo_restante = principal

        while saldo_restante > 0 and mes < plazo_total_meses:
            mes += 1
            interes_mes = saldo_restante * tasa_mensual
            pago_total = pago_mensual_fijo + pago_mensual_adicional

            if saldo_restante + interes_mes < pago_total:
                if pago_mensual_adicional > 0:
                    pago_total = saldo_restante + interes_mes
                pago_principal = saldo_restante
                interes_mes = pago_total - pago_principal
                saldo_restante = 0
            else:
                pago_principal = pago_total - interes_mes
                saldo_restante -= pago_principal

            total_intereses_pagados += interes_mes

            pagos.append((
                mes,
                f"${pago_total:,.2f}",
                f"${interes_mes:,.2f}",
                f"${pago_principal:,.2f}",
                f"${saldo_restante:,.2f}"
            ))

            if saldo_restante == 0:
                break

        # Calculate interest savings
        ahorro_intereses = interes_original - total_intereses_pagados if pago_mensual_adicional > 0 else 0

        resumen = {
            translations[lang]['Total Time']: f"{mes // 12} {translations[lang]['years']}, {mes % 12} {translations[lang]['months']} ({mes} {translations[lang]['months in total']})",
            translations[lang]['Total Interest Paid']: f"${total_intereses_pagados:,.2f}",
            translations[lang]['Total Interest Saved']: f"${ahorro_intereses:,.2f}",
            translations[lang]['Initial Daily Interest']: f"${principal * tasa_diaria:,.2f}",
            translations[lang]['Final Daily Interest']: f"${saldo_restante * tasa_diaria:,.2f}",
            translations[lang]['Original Interest Without Additional Payments']: f"${interes_original:,.2f}",
        }

        df_pagos = pd.DataFrame(pagos, columns=[
            translations[lang]['Month'],
            translations[lang]['Total Monthly Payment'],
            translations[lang]['Interest Payment'],
            translations[lang]['Principal Payment'],
            translations[lang]['Remaining Principal']
        ])

        return df_pagos, resumen

    except Exception as e:
        app.logger.error(f"Error in loan calculation: {str(e)}")
        raise ValueError(f"Error in calculation: {str(e)}")

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

            return render_template(template, resumen=resumen_final, tables=[table_html], form_data=form_data, translations=translations[lang])
        except ValueError as e:
            return render_template(template, error=str(e), form_data=form_data, translations=translations[lang])
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return render_template(template, error="An unexpected error occurred. Please try again.", form_data=form_data, translations=translations[lang])
    return render_template(template, form_data=form_data, translations=translations[lang])

if __name__ == "__main__":
    app.run(debug=True)
    