import pandas as pd

def calcular_prestamo(principal, tasa_anual, pago_mensual_fijo, pago_mensual_adicional=0, max_months=None):
    # Calcula el pago total mensual
    pago_mensual_total = pago_mensual_fijo + pago_mensual_adicional
    
    # Calcula la tasa de interés mensual
    tasa_mensual = tasa_anual / 12 / 100
    
    # Lista para almacenar los resultados mensuales
    pagos = []
    
    # Inicializa variables
    mes = 0
    total_interes_pagado = 0
    
    # Realiza los cálculos mensuales hasta que el préstamo esté pagado
    while principal > 0 and (max_months is None or mes < max_months):
        mes += 1
        # Calcula el interés del mes actual
        pago_interes = principal * tasa_mensual
        pago_principal = pago_mensual_total - pago_interes
        
        # Asegura que no se pague más del saldo restante
        if pago_principal > principal:
            pago_principal = principal
            pago_mensual_total = pago_principal + pago_interes

        # Reduce el principal
        principal -= pago_principal
        total_interes_pagado += pago_interes

        # Guarda los resultados del mes
        pagos.append((
            mes,
            f"${pago_mensual_total:.2f}",
            f"${pago_interes:.2f}",
            f"${pago_principal:.2f}",
            f"${principal:.2f}"
        ))
    
    # Convierte los resultados a un DataFrame de pandas para facilitar la visualización
    df = pd.DataFrame(pagos, columns=["Mes", "Pago Mensual Total", "Pago Interes", "Pago Principal", "Principal Restante"])

    # Calcula el resumen final
    resumen = {
        "Meses Totales": mes,
        "Total Interes Pagado": total_interes_pagado
    }
    
    return df, resumen

# Variables iniciales (sin cambios)
principal_prestamo1 = 19111.47
principal_prestamo2 = 9011.80
principal_prestamo3 = 7226.95

tasa_anual_prestamo1 = 13.75
tasa_anual_prestamo2 = 13.50
tasa_anual_prestamo3 = 14.375

pago_mensual_prestamo2 = 464.77
pago_mensual_prestamo3 = 173.69
pago_mensual_adicional = 453.13

# Paso 1: Pagar el préstamo 1 de inmediato (sin cambios)
interes_pagado_prestamo1 = 0
principal_prestamo1 = 0

# Paso 2 y 3 combinados: Pagar préstamos 2 y 3 simultáneamente, luego redirigir pagos
pagos_combinados = []
mes = 0
while principal_prestamo2 > 0 or principal_prestamo3 > 0:
    mes += 1
    pago_total_mes = pago_mensual_prestamo2 + pago_mensual_prestamo3 + pago_mensual_adicional

    # Préstamo 3
    if principal_prestamo3 > 0:
        pago_interes_p3 = principal_prestamo3 * (tasa_anual_prestamo3 / 12 / 100)
        pago_principal_p3 = min(principal_prestamo3 + pago_interes_p3, pago_mensual_prestamo3 + pago_mensual_adicional)
        principal_prestamo3 = max(0, principal_prestamo3 - (pago_principal_p3 - pago_interes_p3))
        pagos_combinados.append([mes, f"${pago_principal_p3:.2f}", f"${pago_interes_p3:.2f}", f"${pago_principal_p3 - pago_interes_p3:.2f}", f"${principal_prestamo3:.2f}", "Préstamo 3"])
        pago_total_mes -= pago_principal_p3
    
    # Préstamo 2
    if principal_prestamo2 > 0:
        pago_interes_p2 = principal_prestamo2 * (tasa_anual_prestamo2 / 12 / 100)
        pago_principal_p2 = min(principal_prestamo2 + pago_interes_p2, pago_total_mes)
        principal_prestamo2 = max(0, principal_prestamo2 - (pago_principal_p2 - pago_interes_p2))
        pagos_combinados.append([mes, f"${pago_principal_p2:.2f}", f"${pago_interes_p2:.2f}", f"${pago_principal_p2 - pago_interes_p2:.2f}", f"${principal_prestamo2:.2f}", "Préstamo 2"])

# Convierte los resultados a un DataFrame de pandas
df_combined = pd.DataFrame(pagos_combinados, columns=["Mes", "Pago Mensual Total", "Pago Interes", "Pago Principal", "Principal Restante", "Préstamo"])

# Calcula el resumen final
interes_original = 6716.94 + 748.37 + 2673.38
total_interes_pagado = sum(float(row[2].replace('$', '')) for row in pagos_combinados)
ahorro_interes = interes_original - total_interes_pagado

resumen_final = {
    "Meses Totales": mes,
    "Total Interes Pagado": f"${total_interes_pagado:.2f}",
    "Total Interes Ahorrado": f"${ahorro_interes:.2f}"
}

# Muestra los resultados
print("Resumen Final:")
print(f"Meses Totales: {resumen_final['Meses Totales']}")
print(f"Total Interes Pagado: {resumen_final['Total Interes Pagado']}")
print(f"Total Interes Ahorrado: {resumen_final['Total Interes Ahorrado']}")

# Guarda el DataFrame en un archivo CSV
df_combined.to_csv("salimay2_corregido.csv", index=False)

# Muestra el DataFrame
print("\nDetalles de los Pagos Mensuales:")
print(df_combined)
