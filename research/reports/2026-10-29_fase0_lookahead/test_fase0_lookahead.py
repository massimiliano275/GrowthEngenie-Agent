"""Fase 0 — prove eseguibili dei due look-ahead (29/10/2026).

Questi test DEVONO fallire sul codice attuale: sono la prova del problema.
Passeranno solo dopo le correzioni proposte (non applicate) descritte in REPORT.md.

Uso:  python -m pytest test_fase0_lookahead.py -v
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PHOENIX = Path(r"C:\Users\massimiliano\Desktop\GROWTH_ENGENIE_3ST\GrowthEngenie3st\growthengenie3st_backpack\phoenix")


def _phoenix_ingresso(close_barra_ambigua: float):
    """Barra 0 = riferimento (H 110, L 100); barra 1 tocca entrambi i livelli; poi barre neutre."""
    # caricato con un nome proprio: "backtest" come nome di modulo coprirebbe il pacchetto di Vibe-Trading
    spec = importlib.util.spec_from_file_location("phoenix_backtest", PHOENIX / "backtest.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["phoenix_backtest"] = mod      # serve a @dataclass per risolvere il modulo
    spec.loader.exec_module(mod)
    Backtester, BacktestConfig = mod.Backtester, mod.BacktestConfig

    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=4, freq="D"),
        "Open": [105, 105, 105, 105],
        "High": [110, 112, 106, 106],
        "Low": [100, 98, 104, 104],
        "Close": [105, close_barra_ambigua, 105, 105],
    })
    trades, _ = Backtester(df, BacktestConfig(variant="B", k_entry=0.0, k_trail=3.0)).run()
    return trades[0].side, float(trades[0].entry_price)


def test_a_phoenix_barra_ambigua_non_dipende_dalla_chiusura():
    """phoenix/backtest.py:394-399 — il lato non deve dipendere da Close[i]."""
    rialzo = _phoenix_ingresso(111.0)
    ribasso = _phoenix_ingresso(99.0)
    assert rialzo == ribasso, f"look-ahead: chiusura 111 -> {rialzo}, chiusura 99 -> {ribasso}"


def test_b_factor_analysis_segnala_allineamento_stesso_giorno(tmp_path):
    """Vibe-Trading src/factors/factor_analysis_core.py:22-41 — fattore e rendimento della stessa data."""
    import json
    import mcp_server

    rng = np.random.default_rng(0)
    idx = pd.date_range("2026-01-01", periods=60, freq="D")
    ret = pd.DataFrame(rng.normal(0, 0.02, (60, 8)), index=idx, columns=[f"A{i}" for i in range(8)])
    fattore = ret.copy()                      # il fattore E' il rendimento dello stesso giorno
    ret.to_csv(tmp_path / "ret.csv")
    fattore.to_csv(tmp_path / "fattore.csv")

    out = json.loads(mcp_server.factor_analysis(str(tmp_path / "fattore.csv"), str(tmp_path / "ret.csv"),
                                                str(tmp_path / "out"), 5))
    assert out.get("status") != "ok", (
        f"nessun avviso: status={out.get('status')}, ic_mean={out.get('ic_mean')} con rendimenti dello stesso giorno")
