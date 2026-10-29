"""Fase 2A — registratore: cattura input e risultati del motore di ricerca, fold per fold.

Non modifica `sweep_may_vs_fixed.py`: lo importa e intercetta due funzioni.
- `apply_exit`: per ogni asset registra open, high e low della finestra (servono a Vibe-Trading).
- `run_portfolio`: per la variante A (le prime due chiamate di ogni fold: equal, tier) salva
  gli input esatti e il risultato.

Uso (con l'interprete del progetto di ricerca, che ha `requests`):
    python registratore.py <cartella output>

Esegue lo stesso comando della pre-registrazione (errata):
    --wf_filters --wf_exits --tf 4h --asof 2026-10-01
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

RICERCA = Path(r"C:\Users\massimiliano\Desktop\GROWTH_ENGENIE_3ST\GrowthEngenie3st\growthengenie3st_backpack\research\sweep_may_vs_fixed.py")
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("ricerca", RICERCA)
ric = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ric)

_hilo = []                       # (op, hi, lo) di ogni chiamata ad apply_exit
_orig_apply_exit = ric.apply_exit
_orig_run_portfolio = ric.run_portfolio
_stato = {"chiamata": 0, "variants": None}


def apply_exit_reg(sig, op, hi, lo, atr, mode, **kw):
    if mode == "A":
        _hilo.append((np.asarray(op, float).copy(), np.asarray(hi, float).copy(), np.asarray(lo, float).copy()))
    return _orig_apply_exit(sig, op, hi, lo, atr, mode, **kw)


def run_portfolio_reg(assets, keys, sizing, start_i, slot_frac=0.095, tier=(0.40, 0.30, 0.20), bars_per_year=365.25):
    res = _orig_run_portfolio(assets, keys, sizing, start_i, slot_frac=slot_frac, tier=tier, bars_per_year=bars_per_year)
    n_var = 6                                   # A, E1, E2, E3, E3b, E4 con --wf_exits
    k = _stato["chiamata"]
    _stato["chiamata"] += 1
    fold, pos = divmod(k, 2 * n_var)
    if pos < 2:                                 # variante A: pos 0 = equal, pos 1 = tier
        if pos == 0:
            arr = {}
            for tk, a in assets.items():
                op = np.asarray(a["op"], float)
                hl = [h for h in _hilo if len(h[0]) == len(op) and np.array_equal(h[0], op, equal_nan=True)]
                if not hl:
                    raise RuntimeError(f"fold {fold}: high/low non trovati per {tk}")
                arr[f"{tk}__op"] = op
                arr[f"{tk}__hi"] = hl[-1][1]
                arr[f"{tk}__lo"] = hl[-1][2]
                for c in ("cl", "fund", "valid", "mom", "sig"):
                    arr[f"{tk}__{c}"] = np.asarray(a[c], float)
            np.savez_compressed(OUT / f"fold{fold}_input.npz", **arr)
            _hilo.clear()
        r = {kk: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v) for kk, v in res.items()}
        with open(OUT / f"fold{fold}_{sizing}_risultato.json", "w", encoding="utf-8") as f:
            json.dump({"fold": fold, "sizing": sizing, "slot_frac": slot_frac, "tier": list(tier),
                       "bars_per_year": bars_per_year, "asset": list(assets.keys()), **r}, f, indent=1)
    return res


ric.apply_exit = apply_exit_reg
ric.run_portfolio = run_portfolio_reg
sys.argv = ["sweep_may_vs_fixed.py", "--wf_filters", "--wf_exits", "--tf", "4h", "--asof", "2026-10-01"]
ric.main()
print(f"\n[registratore] fold catturati: {len(list(OUT.glob('fold*_input.npz')))} in {OUT}")
