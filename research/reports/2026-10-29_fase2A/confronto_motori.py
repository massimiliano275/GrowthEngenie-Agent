"""Fase 2A — confronto fold per fold: motore di ricerca contro Vibe-Trading, stessi input.

Passi per ogni fold catturato dal registratore (variante A):
 1. fedeltà della cattura: `run_portfolio` del motore di ricerca sui dati catturati deve ridare
    il risultato salvato durante la run originale;
 2. riferimento senza funding: `run_portfolio` con funding a zero;
 3. Vibe-Trading senza funding: stessi prezzi, stessi pesi, commissione 0,05% per lato, slippage 0.

Scelte di metodo:
 - il motore di ricerca decide e compra all'open della stessa barra i; Vibe-Trading esegue all'open
   della barra dopo il segnale: a Vibe-Trading si passa il peso obiettivo della barra i+1 sulla barra i;
 - i pesi arrivano al signal engine come colonna `w` dei dati (il sandbox non permette di leggere file);
 - indice temporale sintetico a 4H (senza funding l'ora non conta);
 - codici spot fittizi `T<n>-USDT`: niente funding, short ammessi.

Uso (interprete di Vibe-Trading):
    python confronto_motori.py <cartella catture> <cartella run>
"""
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RICERCA = Path(r"C:\Users\massimiliano\Desktop\GROWTH_ENGENIE_3ST\GrowthEngenie3st\growthengenie3st_backpack\research\sweep_may_vs_fixed.py")
CATTURE = Path(sys.argv[1]).resolve()
RUNS = Path(sys.argv[2]).resolve()
RUNS.mkdir(parents=True, exist_ok=True)

_stdout = sys.stdout
spec = importlib.util.spec_from_file_location("ricerca", RICERCA)
ric = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ric)
# il modulo riavvolge sys.stdout in un TextIOWrapper: se l'involucro venisse distrutto
# chiuderebbe il buffer sottostante, quindi resta referenziato e si usa quello
_WRAP_RICERCA = sys.stdout

SIGNAL_ENGINE = '''"""Pesi obiettivo calcolati fuori dal motore (colonna w), eseguiti all'open della barra dopo."""

from typing import Dict

import pandas as pd


class SignalEngine:
    def generate(self, data_map: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        return {code: df["w"].astype(float) for code, df in data_map.items()}
'''


def carica_fold(p):
    z = np.load(p)
    tks = sorted({k.split("__")[0] for k in z.files})
    return {tk: {c: z[f"{tk}__{c}"] for c in ("op", "hi", "lo", "cl", "fund", "valid", "mom", "sig")} for tk in tks}


def assets_ricerca(d, con_funding):
    out = {}
    for tk, a in d.items():
        out[tk] = {"op": a["op"], "cl": a["cl"], "fund": a["fund"] if con_funding else np.zeros_like(a["fund"]),
                   "valid": a["valid"].astype(bool), "mom": a["mom"], "sig": a["sig"].astype(int)}
    return out


def pesi_obiettivo(d, sizing, slot_frac, tier):
    """Copia della regola di `run_portfolio`: target alla barra i (eseguito all'open di i)."""
    tks = list(d)
    n = len(next(iter(d.values()))["op"])
    w = {tk: np.zeros(n) for tk in tks}
    for i in range(1, n):
        active = [tk for tk in tks if d[tk]["valid"][i] and d[tk]["sig"][i] != 0]
        if sizing == "tier":
            ranked = sorted(active, key=lambda tk: d[tk]["sig"][i] * d[tk]["mom"][i], reverse=True)[:3]
            for j, tk in enumerate(ranked):
                w[tk][i] = d[tk]["sig"][i] * tier[j]
        else:
            for tk in active:
                w[tk][i] = d[tk]["sig"][i] * slot_frac
    return w


def run_vibe(d, w, run_dir):
    from backtest import runner
    from backtest.loaders import binance_loader

    n = len(next(iter(d.values()))["op"])
    idx = pd.date_range("2020-01-01", periods=n, freq="4h", name="trade_date")
    frames, mappa = {}, {}
    for k, (tk, a) in enumerate(d.items()):
        code = f"T{k:02d}-USDT"
        mappa[code] = tk
        hi = np.maximum.reduce([a["hi"], a["op"], a["cl"]])
        lo = np.minimum.reduce([a["lo"], a["op"], a["cl"]])
        # peso obiettivo della barra i+1 sulla barra i: Vibe-Trading lo esegue all'open di i+1
        ws = np.r_[w[tk][1:], 0.0]
        frames[code] = pd.DataFrame({"open": a["op"], "high": hi, "low": lo, "close": a["cl"],
                                     "volume": 1.0, "w": ws}, index=idx)

    def fetch(self, codes, start_date, end_date, interval="1D", **kw):
        return {c: frames[c] for c in codes if c in frames}

    binance_loader.DataLoader.fetch = fetch
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "code").mkdir(exist_ok=True)
    (run_dir / "code" / "signal_engine.py").write_text(SIGNAL_ENGINE, encoding="utf-8")
    cfg = {"source": "binance", "codes": list(frames), "start_date": str(idx[0].date()),
           "end_date": str(idx[-1].date()), "interval": "4H", "initial_cash": 1000,
           "maker_rate": 0.0005, "taker_rate": 0.0005, "slippage": 0.0, "funding_rate": 0.0, "leverage": 1}
    (run_dir / "config.json").write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            runner.main(run_dir)
        except SystemExit:
            pass
    eq = pd.read_csv(run_dir / "artifacts" / "equity.csv")
    fills = [json.loads(x) for x in open(run_dir / "artifacts" / "fills.jsonl", encoding="utf-8")]
    aperture = sum(1 for f in fills if f.get("action") == "open")
    somma = pd.DataFrame(w).abs().sum(axis=1)
    return {"final": float(eq["equity"].iloc[-1]), "ret": (float(eq["equity"].iloc[-1]) / 1000 - 1) * 100,
            "trades": aperture, "barre_oltre_100pct": int((somma > 1.0 + 1e-9).sum()), "barre": n}


righe = []
for p in sorted(CATTURE.glob("fold*_input.npz")):
    fold = int(p.stem.split("_")[0][4:])
    d = carica_fold(p)
    for sizing in ("equal", "tier"):
        salvato = json.load(open(CATTURE / f"fold{fold}_{sizing}_risultato.json", encoding="utf-8"))
        sf, tier = salvato["slot_frac"], tuple(salvato["tier"])
        rif_con = ric.run_portfolio(assets_ricerca(d, True), list(d), sizing, 1, slot_frac=sf, tier=tier)
        rif_senza = ric.run_portfolio(assets_ricerca(d, False), list(d), sizing, 1, slot_frac=sf, tier=tier)
        w = pesi_obiettivo(d, sizing, sf, tier)
        vt = run_vibe(d, w, RUNS / f"fold{fold}_{sizing}")
        righe.append({
            "fold": fold, "sizing": sizing, "asset": len(d), "barre": vt["barre"],
            "cattura_ok": abs(rif_con["ret"] - salvato["ret"]) < 1e-9 and rif_con["trades"] == salvato["trades"],
            "ricerca_ret_con_funding": round(rif_con["ret"], 4),
            "ricerca_ret_senza_funding": round(rif_senza["ret"], 4),
            "vibe_ret_senza_funding": round(vt["ret"], 4),
            "diff_pp": round(vt["ret"] - rif_senza["ret"], 4),
            "ricerca_trades": int(rif_senza["trades"]), "vibe_trades": vt["trades"],
            "barre_esposizione_oltre_100pct": vt["barre_oltre_100pct"],
        })
        print(json.dumps(righe[-1]), flush=True)

pd.DataFrame(righe).to_csv(RUNS / "confronto_fold.csv", index=False)
print(f"\nsalvato: {RUNS / 'confronto_fold.csv'}")
