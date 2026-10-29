"""Fase 2C — 52 run: {5 slot x 19%, 10 slot x 9,5%} x 26 date di partenza (ogni 14 giorni).

Codice di base: traduzione del 25/10 (uscita sul flip ST 4H a candela chiusa), con le sole costanti
N_MAX_SLOTS, SLOT_SIZE e SIM_START sostituite. Ogni run passa dal lanciatore listing-safe.

Uso (interprete di Vibe-Trading):
    python batch.py <cartella vibe_trading> <cartella runs di output>
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

VT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
BASE_CODE = (VT / "runs" / "backpack_4h" / "code" / "signal_engine.py").read_text(encoding="utf-8")
BASE_CFG = json.loads((VT / "runs" / "backpack_4h" / "config.json").read_text(encoding="utf-8"))
DATA_START = pd.Timestamp("2024-05-01")
STARTS = [pd.Timestamp("2024-07-01") + pd.Timedelta(days=14 * k) for k in range(26)]
CONFIGS = [(5, 0.19), (10, 0.095)]


def codice(n, size, start):
    c = re.sub(r"^N_MAX_SLOTS = \d+ ", f"N_MAX_SLOTS = {n} ", BASE_CODE, count=1, flags=re.M)
    c = re.sub(r"^SLOT_SIZE = [0-9.]+ ", f"SLOT_SIZE = {size} ", c, count=1, flags=re.M)
    c = re.sub(r'^SIM_START = "[0-9-]+"', f'SIM_START = "{start:%Y-%m-%d}"', c, count=1, flags=re.M)
    for chiave, val in (("N_MAX_SLOTS", str(n)), ("SLOT_SIZE", str(size)), ("SIM_START", f'"{start:%Y-%m-%d}"')):
        if not re.search(rf"^{chiave} = {re.escape(val)}", c, flags=re.M):
            raise RuntimeError(f"sostituzione fallita: {chiave}")
    return c


def metriche(run_dir):
    a = run_dir / "artifacts"
    m = pd.read_csv(a / "metrics.csv").iloc[0]
    t = pd.read_csv(a / "trades.csv")
    x = t[t.event == "exit"].copy()
    x["ts"] = pd.to_datetime(x.timestamp)
    zec = x[(x.code == "ZEC-USDT-PERP") & (x.side == "sell") & (x.return_pct >= 100)
            & (x.ts >= "2025-09-01") & (x.ts <= "2026-03-31")]
    tp = pd.read_csv(a / "target_positions.csv", index_col=0)
    return {"rend_tot": m.total_return * 100, "rend_annuo": m.annual_return * 100, "max_dd": m.max_drawdown * 100,
            "sharpe": m.sharpe, "trade": int(m.trade_count), "durata_media_gg": m.avg_holding_days,
            "catture_100pct": int((x.return_pct >= 100).sum()), "zec_long_preso": int(len(zec) > 0),
            "posiz_max": int((tp.abs() > 1e-9).sum(axis=1).max()), "finale": m.final_value}


def esegui(start, n, size):
    nome = f"s{n:02d}_{start:%Y%m%d}"
    rd = OUT / nome
    (rd / "code").mkdir(parents=True, exist_ok=True)
    (rd / "code" / "signal_engine.py").write_text(codice(n, size, start), encoding="utf-8")
    cfg = dict(BASE_CFG)
    cfg["warmup_bars"] = int((start - DATA_START).days * 6)
    cfg["title"] = f"Fase 2C {n} slot x {size*100:g}% uscita 4H, partenza {start:%Y-%m-%d}"
    (rd / "config.json").write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    if not (rd / "artifacts" / "metrics.csv").exists():
        env = dict(os.environ, VIBE_TRADING_ALLOWED_RUN_ROOTS=str(OUT), PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, str(VT / "tools" / "run_backtest_listing_safe.py"), str(rd)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        (rd / "run.log").write_text(p.stdout[-20000:] + "\n" + p.stderr[-20000:], encoding="utf-8")
    try:
        return {"partenza": f"{start:%Y-%m-%d}", "slot": n, **metriche(rd)}
    except Exception as e:
        return {"partenza": f"{start:%Y-%m-%d}", "slot": n, "errore": str(e)[:200]}


# 6 run in parallelo: ogni run e' un processo separato, il lavoro e' di CPU
from concurrent.futures import ThreadPoolExecutor, as_completed

righe = []
with ThreadPoolExecutor(max_workers=int(os.environ.get("FASE2C_WORKERS", "6"))) as ex:
    futuri = [ex.submit(esegui, start, n, size) for start in STARTS for n, size in CONFIGS]
    for f in as_completed(futuri):
        r = f.result()
        righe.append(r)
        print(json.dumps(r, default=float), flush=True)
        pd.DataFrame(righe).sort_values(["partenza", "slot"]).to_csv(OUT / "risultati_fase2C.csv", index=False)

print(f"\nfatto: {len(righe)} run -> {OUT / 'risultati_fase2C.csv'}")
