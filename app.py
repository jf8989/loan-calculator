from flask import Flask, request, render_template
import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)

def calcular_prestamo(principal, tasa_anual, pago_mensual_fijo, pago_mensual_adicional, plazo_anios, plazo_meses):
    # Convertir las entradas a tipos numéricos
    principal = float(principal.replace('$', '').replace(',', ''))
    tasa_anual = float(tasa_anual.replace('%', ''))
    pago_mensual_fijo = float(pago_mensual_fijo.replace('$', '').replace(',', ''))
    pago_mensual_adicional = float(pago_mensual_adicional.replace('$', '').replace(',', ''))
    plazo_anios = int(plazo_anios)
    plazo_meses = int(plazo_meses)

    # Calcular el pago mensual total
    pago_mensual_total = pago_mensual_fijo + pago_mensual_adicional
    
    # Calcular la tasa de interés mensual
    tasa_mensual = tasa_anual / 12 / 100
    
    # Calcular la tasa de interés diaria (aproximadamente)
    tasa_diaria = tasa_anual / 365 / 100
    
    # Lista para almacenar los resultados mensuales
    pagos = []
    
    # Inicializar variables
    mes = 0
    total_intereses_pagados = 0
    interes_diario_inicial = principal * tasa_diaria
    interes_diario_final = 0
    
    # Realizar los cálculos mensuales hasta que el préstamo esté pagado
    while principal > 0:
        mes += 1
        # Calcular el interés del mes actual
        pago_interes = principal * tasa_mensual
        pago_principal = pago_mensual_total - pago_interes
        
        # Asegurarse de no pagar más del saldo restante
        if pago_principal > principal:
            pago_principal = principal
            pago_mensual_total = pago_principal + pago_interes

        # Reducir el principal
        principal -= pago_principal
        total_intereses_pagados += pago_interes
        
        # Actualizar el interés diario final
        interes_diario_final = principal * tasa_diaria

        # Guardar los resultados del mes
        pagos.append((
            mes,
            f"${pago_mensual_total:.2f}",
            f"${pago_interes:.2f}",
            f"${pago_principal:.2f}",
            f"${principal:.2f}"
        ))
    
    # Convertir los resultados a un DataFrame de pandas para facilitar la visualización
    df = pd.DataFrame(pagos, columns=["Mes", "Pago Mensual Total", "Pago Intereses", "Pago Principal", "Principal Restante"])

    # Calcular el interés a pagar si se espera hasta el final del plazo original
    plazo_total_meses = plazo_anios * 12 + plazo_meses
    principal_original = principal + sum([float(pago[3].replace('$','')) for pago in pagos])
    pago_mensual_original = principal_original * tasa_mensual / (1 - (1 + tasa_mensual) ** -plazo_total_meses)
    interes_a_pagar_si_se_espera = 0
    principal_temp = principal_original

    for _ in range(plazo_total_meses):
        pago_interes_temp = principal_temp * tasa_mensual
        pago_principal_temp = pago_mensual_original - pago_interes_temp
        principal_temp -= pago_principal_temp
        interes_a_pagar_si_se_espera += pago_interes_temp

    ahorro_intereses = interes_a_pagar_si_se_espera - total_intereses_pagados

    # Calcular el tiempo total en años y meses
    tiempo_total_anios = mes // 12
    tiempo_total_meses = mes % 12

    resumen = {
    "Tiempo Total": f"{tiempo_total_anios} años, {tiempo_total_meses} meses",
    "Total Intereses Pagados": locale.currency(total_intereses_pagados, grouping=True),
    "Total Intereses Ahorrados": locale.currency(ahorro_intereses, grouping=True),
    "Interés Diario Inicial": locale.currency(interes_diario_inicial, grouping=True),
    "Interés Diario Final": locale.currency(interes_diario_final, grouping=True)
}
    
    return df, resumen

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            principal = request.form["principal"]
            tasa_anual = request.form["tasa_anual"]
            pago_mensual_fijo = request.form["pago_mensual_fijo"]
            pago_mensual_adicional = request.form["pago_mensual_adicional"]
            plazo_anios = request.form["plazo_anios"]
            plazo_meses = request.form["plazo_meses"]

            df_pagos, resumen_final = calcular_prestamo(principal, tasa_anual, pago_mensual_fijo, pago_mensual_adicional, plazo_anios, plazo_meses)

            return render_template("index.html", resumen=resumen_final, tables=[df_pagos.to_html(classes='data')], request=request)
        except Exception as e:
            print(f"Error: {e}")
            app.logger.error(f"An error occurred: {str(e)}")
            return render_template("index.html", error="Hubo un error procesando tu solicitud. Por favor, verifica los datos ingresados.", request=request)
    return render_template("index.html", request=request)

if __name__ == "__main__":
    app.run(debug=True)