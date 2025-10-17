# Path: tests/test_amortization.py
import re
import math
import pytest

from app import calcular_prestamo  # imports the function only

def money_to_float(s: str) -> float:
    return float(s.replace("$", "").replace(",", ""))

def parse_months_from_resumen(resumen: dict, lang: str) -> int:
    key = "Total Time" if lang == "en" else "Tiempo Total"
    # format: "X years, Y months (Z months in total)"  /  "X años, Y meses (Z meses en total)"
    txt = resumen[key]
    m = re.search(r"\((\d+)\s", txt)
    assert m, f"Could not parse months from '{txt}'"
    return int(m.group(1))

def monthly_rate(apr_percent: float) -> float:
    return apr_percent / 12.0 / 100.0

# ---------- Exact scenario checks ----------

def test_baseline_no_extras():
    # Test 1 exact numbers
    df, resumen = calcular_prestamo(
        principal="$10,000.00",
        tasa_anual="12%",
        pago_mensual_fijo="$0.00",      # let function use the computed base payment
        pago_mensual_adicional="$0.00",
        plazo_anios="2",
        plazo_meses="0",
        lang="en",
    )
    months = parse_months_from_resumen(resumen, "en")
    assert months == 24

    paid = money_to_float(resumen["Total Interest Paid"])
    orig = money_to_float(resumen["Original Interest Without Additional Payments"])

    assert round(paid, 2) == 1297.63
    assert round(orig, 2) == 1297.63
    assert len(df) == 24

def test_with_extra_payment():
    # Test 2 exact numbers
    df, resumen = calcular_prestamo(
        principal="$10,000.00",
        tasa_anual="12%",
        pago_mensual_fijo="$0.00",
        pago_mensual_adicional="$100.00",
        plazo_anios="2",
        plazo_meses="0",
        lang="en",
    )
    months = parse_months_from_resumen(resumen, "en")
    paid = money_to_float(resumen["Total Interest Paid"])
    saved = money_to_float(resumen["Total Interest Saved"])
    orig = money_to_float(resumen["Original Interest Without Additional Payments"])

    assert months == 20
    assert round(paid, 2) == 1049.58
    assert round(saved, 2) == 248.05
    assert round(orig, 2) == 1297.63
    assert len(df) == 20

def test_zero_percent_apr():
    df, resumen = calcular_prestamo(
        principal="$1,200.00",
        tasa_anual="0%",
        pago_mensual_fijo="$100.00",
        pago_mensual_adicional="$20.00",
        plazo_anios="1",
        plazo_meses="0",
        lang="en",
    )
    months = parse_months_from_resumen(resumen, "en")
    assert months == 10
    assert money_to_float(resumen["Total Interest Paid"]) == 0.0
    assert money_to_float(resumen["Original Interest Without Additional Payments"]) == 0.0
    assert len(df) == 10

def test_negative_amortization_rejected():
    with pytest.raises(ValueError):
        calcular_prestamo(
            principal="$50,000.00",
            tasa_anual="18%",
            pago_mensual_fijo="$700.00",   # monthly interest ~ $750 -> should fail
            pago_mensual_adicional="$0.00",
            plazo_anios="5",
            plazo_meses="0",
            lang="en",
        )

# ---------- Invariants on a standard schedule ----------

def test_monotonic_balance_and_interest_formula():
    principal = "$10,000.00"
    apr = 12.0
    df, _ = calcular_prestamo(
        principal=principal,
        tasa_anual=f"{apr}%",
        pago_mensual_fijo="$0.00",
        pago_mensual_adicional="$0.00",
        plazo_anios="2",
        plazo_meses="0",
        lang="en",
    )

    r = monthly_rate(apr)
    prev_balance = money_to_float(principal)
    for i, row in df.iterrows():
        interest = money_to_float(row["Interest Payment"])
        remaining = money_to_float(row["Remaining Principal"])

        # interest ≈ previous balance * r (within 2 cents)
        assert abs(interest - prev_balance * r) < 0.02

        # balance never increases
        assert remaining <= prev_balance + 1e-6

        prev_balance = remaining

    # last balance is exactly zero (after formatting)
    assert money_to_float(df.iloc[-1]["Remaining Principal"]) == 0.0
