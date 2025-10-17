import re
import math
import pytest
from hypothesis import given, strategies as st, settings

from app import calcular_prestamo

def money_to_float(s: str) -> float:
    return float(s.replace("$", "").replace(",", ""))

def parse_months_from_resumen(resumen: dict, lang: str) -> int:
    key = "Total Time" if lang == "en" else "Tiempo Total"
    txt = resumen[key]
    m = re.search(r"\((\d+)\s", txt)
    assert m, f"Could not parse months from '{txt}'"
    return int(m.group(1))

# Hypothesis strategies
st_principal = st.floats(min_value=100.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False)
st_apr = st.floats(min_value=0.0, max_value=40.0, allow_nan=False, allow_infinity=False)
st_years = st.integers(min_value=1, max_value=40)
st_months = st.integers(min_value=0, max_value=11)
st_extra = st.floats(min_value=0.0, max_value=5000.0, allow_nan=False, allow_infinity=False)

@settings(max_examples=200)
@given(L=st_principal, apr=st_apr, years=st_years, months=st_months, extra=st_extra)
def test_pays_off_within_term_and_no_more_interest_than_baseline(L, apr, years, months, extra):
    """
    Use computed base payment (by passing fixed=0) so schedule is valid; then add 'extra'.
    Invariants:
      - payoff months <= entered term (with extra it should be <= n)
      - total interest paid <= original interest baseline
      - remaining principal monotonically decreases
      - last balance is exactly 0.00
    """
    n = years * 12 + months
    # Format inputs exactly as the app receives them
    df, resumen = calcular_prestamo(
        principal=f"${L:,.2f}",
        tasa_anual=f"{apr:.2f}%",
        pago_mensual_fijo="$0.00",          # let function compute the base payment
        pago_mensual_adicional=f"${extra:,.2f}",
        plazo_anios=str(years),
        plazo_meses=str(months),
        lang="en"
    )

    months_used = parse_months_from_resumen(resumen, "en")
    assert 1 <= months_used <= n

    paid = money_to_float(resumen["Total Interest Paid"])
    orig = money_to_float(resumen["Original Interest Without Additional Payments"])
    assert paid <= orig + 0.02  # allow rounding slack

    # Monotonic balance and final zero
    prev = money_to_float(f"${L:,.2f}")
    for _, row in df.iterrows():
        remaining = money_to_float(row["Remaining Principal"])
        assert remaining <= prev + 1e-6
        prev = remaining
    assert money_to_float(df.iloc[-1]["Remaining Principal"]) == 0.0

@settings(max_examples=100)
@given(L=st_principal, years=st_years, months=st_months, extra=st_extra)
def test_zero_apr_no_interest(L, years, months, extra):
    df, resumen = calcular_prestamo(
        principal=f"${L:,.2f}",
        tasa_anual="0%",
        pago_mensual_fijo="$0.00",          # base payment = L / n
        pago_mensual_adicional=f"${extra:,.2f}",
        plazo_anios=str(years),
        plazo_meses=str(months),
        lang="en"
    )
    assert money_to_float(resumen["Total Interest Paid"]) == 0.0
    assert money_to_float(resumen["Original Interest Without Additional Payments"]) == 0.0
    assert money_to_float(df.iloc[-1]["Remaining Principal"]) == 0.0
