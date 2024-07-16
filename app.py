from flask import Flask, request, render_template
import pandas as pd
import locale
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def calcular_prestamo(principal, tasa_anual, pago_mensual_fijo, pago_mensual_adicional, plazo_anios, plazo_meses):
    try:
        # Convert inputs to appropriate types
        principal = float(principal.replace('$', '').replace(',', ''))
        tasa_anual = float(tasa_anual.replace('%', ''))
        pago_mensual_fijo = float(pago_mensual_fijo.replace('$', '').replace(',', ''))
        pago_mensual_adicional = float(pago_mensual_adicional.replace('$', '').replace(',', ''))
        plazo_total_meses = int(plazo_anios) * 12 + int(plazo_meses)

        # Calculate monthly interest rate
        tasa_mensual = tasa_anual / 12 / 100

        # Calculate daily interest rate (not used in this calculation but kept for completeness)
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
                # Pay the remaining balance with interest, adjust for last month with additional payments
                if pago_mensual_adicional > 0:
                    pago_total = saldo_restante + interes_mes
                pago_principal = saldo_restante
                interes_mes = pago_total - pago_principal  # Adjust interest to match the final payment
                saldo_restante = 0
            else:
                pago_principal = pago_total - interes_mes
                saldo_restante -= pago_principal

            total_intereses_pagados += interes_mes

            pagos.append((
                mes,
                locale.currency(pago_total, grouping=True),
                locale.currency(interes_mes, grouping=True),
                locale.currency(pago_principal, grouping=True),
                locale.currency(saldo_restante, grouping=True)
            ))

            logging.debug(f"Month {mes}: Pago Total = {locale.currency(pago_total, grouping=True)}, Interes Mes = {locale.currency(interes_mes, grouping=True)}, Pago Principal = {locale.currency(pago_principal, grouping=True)}, Saldo Restante = {locale.currency(saldo_restante, grouping=True)}")

            if saldo_restante == 0:
                break

        # Provide feedback about extra interest paid if no additional payments
        if pago_mensual_adicional == 0 and round(total_intereses_pagados, 2) != round(interes_original, 2):
            extra_interest = total_intereses_pagados - interes_original
            feedback = f"Due to the fixed monthly payment, you will end up paying an additional {locale.currency(extra_interest, grouping=True)} in interest."
        else:
            feedback = ""

        # Calculate interest savings only if there are additional payments
        ahorro_intereses = interes_original - total_intereses_pagados if pago_mensual_adicional > 0 else 0

        resumen = {
            "Tiempo Total": f"{mes // 12} años, {mes % 12} meses ({mes} meses en total)",
            "Total Intereses Pagados": locale.currency(total_intereses_pagados, grouping=True),
            "Total Intereses Ahorrados": locale.currency(ahorro_intereses, grouping=True),
            "Interés Diario Inicial": locale.currency(principal * tasa_diaria, grouping=True),
            "Interés Diario Final": locale.currency(saldo_restante * tasa_diaria, grouping=True),
            "Interés Original Sin Pagos Adicionales": locale.currency(interes_original, grouping=True),
            "Feedback": feedback
        }

        return pd.DataFrame(pagos, columns=["Mes", "Pago Mensual Total", "Pago Intereses", "Pago Principal", "Principal Restante"]), resumen

    except Exception as e:
        app.logger.error(f"Error en el cálculo del préstamo: {str(e)}")
        raise ValueError(f"Error en el cálculo: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def index():
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
                form_data["plazo_meses"]
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

            return render_template("index.html", resumen=resumen_final, tables=[table_html], form_data=form_data)
        except ValueError as e:
            return render_template("index.html", error=str(e), form_data=form_data)
        except Exception as e:
            app.logger.error(f"Error inesperado: {str(e)}")
            return render_template("index.html", error="Ocurrió un error inesperado. Por favor, intente nuevamente.", form_data=form_data)
    return render_template("index.html", form_data=form_data)

if __name__ == "__main__":
    app.run(debug=True)
