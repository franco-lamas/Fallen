"""
Fallen Financial Tools — Standalone Test Suite
=================================================
Ejecutar desde la raíz del proyecto:
    python .test/run_tests.py

No requiere pytest ni ningún framework externo.
Cada test verifica que la función devuelva un DataFrame con datos.
Los resultados se guardan en .test/results.json para el resumen posterior.
"""

import sys
import os
import json
import traceback
import time

# ── Ajuste de path para importar el paquete desde la raíz del proyecto ──────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from Fallen import yahoo, ambito, rava, macrotrends, cohen

# ── Colores ANSI ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

# ── Rangos de fecha para los tests ───────────────────────────────────────────
DATE_START = "2024-01-02"
DATE_END   = "2024-03-01"

results = {}


def run_test(name: str, fn):
    """Ejecuta fn(), captura resultado o excepción y registra en `results`."""
    print(f"  {BOLD}→ {name}{RESET} ... ", end="", flush=True)
    t0 = time.time()
    try:
        result = fn()
        elapsed = round(time.time() - t0, 2)
        if isinstance(result, pd.DataFrame) and not result.empty:
            status = "OK"
            detail = f"{len(result)} filas × {len(result.columns)} cols"
            print(f"{GREEN}OK{RESET}  ({detail}, {elapsed}s)")
        elif isinstance(result, pd.DataFrame) and result.empty:
            status = "EMPTY"
            detail = "DataFrame vacío"
            print(f"{YELLOW}EMPTY{RESET}  ({elapsed}s)")
        elif result is not None:
            status = "OK"
            detail = str(type(result))
            print(f"{GREEN}OK{RESET}  ({detail}, {elapsed}s)")
        else:
            status = "NONE"
            detail = "La función devolvió None"
            print(f"{YELLOW}NONE{RESET}  ({elapsed}s)")
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        status = "ERROR"
        detail = f"{type(exc).__name__}: {exc}"
        tb = traceback.format_exc()
        print(f"{RED}ERROR{RESET}  ({elapsed}s)")
        print(f"       {RED}{detail}{RESET}")

    results[name] = {"status": status, "detail": detail, "elapsed": elapsed}


# ─────────────────────────────────────────────────────────────────────────────
# YAHOO FINANCE
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}── Yahoo Finance ──────────────────────────────────────{RESET}")

run_test(
    "yahoo.get_history (GGAL.BA)",
    lambda: yahoo.get_history("GGAL.BA", DATE_START, DATE_END),
)

run_test(
    "yahoo.get_history (MSFT)",
    lambda: yahoo.get_history("MSFT", DATE_START, DATE_END),
)

# ─────────────────────────────────────────────────────────────────────────────
# AMBITO FINANCIERO
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}── Ambito Financiero ──────────────────────────────────{RESET}")

# Ambito usa formato DD-MM-YYYY en la URL (la clase lo convierte internamente)
AMB_START = "2024-01-02"
AMB_END   = "2024-03-01"

run_test(
    "ambito.dolar_blue",
    lambda: ambito.dolar_blue(AMB_START, AMB_END),
)

run_test(
    "ambito.dolar_oficial",
    lambda: ambito.dolar_oficial(AMB_START, AMB_END),
)

run_test(
    "ambito.dolar_solidario",
    lambda: ambito.dolar_solidario(AMB_START, AMB_END),
)

# ─────────────────────────────────────────────────────────────────────────────
# RAVA BURSÁTIL
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}── Rava Bursátil ──────────────────────────────────────{RESET}")

run_test(
    "rava.get_history (GGAL)",
    lambda: rava.get_history("GGAL", DATE_START, DATE_END),
)

run_test(
    "rava.get_history (PAMP)",
    lambda: rava.get_history("PAMP", DATE_START, DATE_END),
)

# ─────────────────────────────────────────────────────────────────────────────
# MACROTRENDS
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}── Macrotrends ────────────────────────────────────────{RESET}")

run_test(
    "macrotrends.get_symbols",
    lambda: macrotrends.get_symbols(),
)

run_test(
    "macrotrends.history (SPY)",
    lambda: macrotrends.history("SPY"),
)

run_test(
    "macrotrends.incomes (AAPL, Q)",
    lambda: macrotrends.incomes("AAPL", freq="Q"),
)

run_test(
    "macrotrends.incomes (AAPL, A)",
    lambda: macrotrends.incomes("AAPL", freq="A"),
)

# ─────────────────────────────────────────────────────────────────────────────
# COHEN
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}── Cohen & Cia ────────────────────────────────────────{RESET}")

run_test(
    "cohen.stocks (GGAL)",
    lambda: cohen.stocks("GGAL", DATE_START, DATE_END),
)

run_test(
    "cohen.cedears (AAPL)",
    lambda: cohen.cedears("AAPL", DATE_START, DATE_END),
)

run_test(
    "cohen.fixed_income (PARP)",
    lambda: cohen.fixed_income("PARP", DATE_START, DATE_END),
)

run_test(
    "cohen.options (GGALC4)",
    lambda: cohen.options("GGALC4", DATE_START, DATE_END),
)

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────────────────────
total  = len(results)
ok     = sum(1 for r in results.values() if r["status"] == "OK")
errors = sum(1 for r in results.values() if r["status"] == "ERROR")
other  = total - ok - errors

print(f"\n{BOLD}{'─'*54}")
print(f"  Resultados: {ok}/{total} OK  |  {errors} ERROR  |  {other} EMPTY/NONE")
print(f"{'─'*54}{RESET}")

# Guardar resultados como JSON para que el script de resumen los consuma
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n  Resultados guardados en: {out_path}\n")
