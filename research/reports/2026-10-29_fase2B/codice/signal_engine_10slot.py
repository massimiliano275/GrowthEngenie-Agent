"""GrowthEngenie3ST — produzione al 29/10/2026 (commit 10ce75a), Fase 2B. Slot e peso: costanti sotto.

Pre-registrazione: GrowthEngenie-Agent/research/preregistration/2026-10-29_fase2B_produzione_5_vs_10_slot.md

Fonti tradotte (repo growthengenie3st_backpack):
  core/sniper_engine.py   _supertrend, _rs_1bar, scan_single_st_1h, _rank_score_single_st_1h,
                          rank_single_st_1h_candidates, _has_daily_confirmation, _is_in_trend_leader
  core/portfolio_5slot.py slot a dimensione fissa, on_position_closed -> rescan_and_fill
  core/asset_strategy.py  evaluate(live_exit=True) con TIMEFRAME "1d" (config della VM, 29/10):
                          si esce quando il ST(6,2) GIORNALIERO sulla candela in formazione e' opposto
                          alla posizione; segnale non disponibile -> si tiene

Ricostruzione dell'uscita: a ogni chiusura 4H, candela del giorno parziale (open del giorno, max e min
fin li', close 4H corrente) e un passo della ricorsione di _supertrend dallo stato dell'ultimo giorno
chiuso. La produzione la valuta ogni minuto: qui una volta per barra 4H.

Approssimazioni dichiarate (non sono scelte di strategia):
  - ST sull'intera storia invece che sulla finestra di 720 barre 4H / 119 1D / 100 1D (uscita):
    differisce solo nell'innesco dell'ATR (fedelta' misurata 100% il 25/10 sullo scan)
  - 1D ricostruito dalle barre 4H Binance (stessa griglia UTC 00:00 delle klines 1d)
  - uscita non disponibile finche' non ci sono piu' di ST_PERIOD giorni chiusi

Il segnale emesso e' il PESO obiettivo (+/-SLOT_SIZE): Vibe-Trading lo esegue all'apertura
della barra successiva, cioe' subito dopo la chiusura 4H.
"""

from typing import Dict, List

import numpy as np
import pandas as pd

# Ordine di config/assets.json::_backpack_all_perps dopo il filtro di _get_perp_symbols:
# decide gli spareggi come in produzione (sort stabili su questa lista).
UNIVERSE = (
    "BTC", "SOL", "ETH", "HYPE", "BNB", "LIT", "TAO", "ZEC", "SUI", "XRP", "PUMP", "AAVE",
    "DOGE", "PENGU", "LINEA", "ENA", "ADA", "ASTER", "APT", "WIF", "UNI", "EDGE", "VIRTUAL",
    "LINK", "CRV", "ARB", "WLFI", "FARTCOIN", "WLD", "LTC", "XPL", "OP", "SKR", "LDO", "DOT",
    "AVAX", "NEAR", "TRUMP", "TON", "S", "AERO", "SEI", "IP", "AVNT", "ONDO", "MET", "BERA",
    "2Z", "TIA", "XLM", "KMNO", "JTO", "PENDLE", "ZORA", "0G", "HBAR", "XMR", "KAITO", "PYTH",
    "STRK", "FOGO", "W", "CC", "VVV",
)

ST_PERIOD, ST_MULT = 6, 2.0            # SINGLE_ST_1H_PERIOD / _MULT
N_MAX_SLOTS = 10                        # Fase 2B: configurazione scelta dall'utente (5) / riferimento (10)
SLOT_SIZE = 0.095                       # 19% per slot con 5 slot, 9,5% con 10
APPENA_MAX_BARS = 2                     # sniper_engine._APPENA_MAX_BARS
CONFERMATI_MAX_BARS = 3                 # sniper_engine._CONFERMATI_MAX_BARS
IN_TREND_RS_MIN_PCT = 1.0               # sniper_engine.IN_TREND_RS_MIN_PCT
IN_TREND_VOL_MIN_PCT = 25.0             # sniper_engine.IN_TREND_VOL_MIN_PCT
MIN_4H_BARS = 120                       # scan: `if df is None or len(df) < 120: continue`
MIN_1D_CLOSED = 49                      # _fetch_1d: None se klines < 50 (49 chiuse + 1 aperta)
SIM_START = "2024-07-01"                # slot vuoti a questa data, come un avvio da zero
BTC_CODE = "BTC-USDT-PERP"


def _supertrend(cl, hi, lo, period, mult):
    """Copia esatta di core/sniper_engine.py::_supertrend."""
    n = len(cl)
    tr = np.zeros(n)
    for i in range(1, n):
        tr[i] = max(hi[i]-lo[i], abs(hi[i]-cl[i-1]), abs(lo[i]-cl[i-1]))
    atr = np.zeros(n)
    if n > period:
        atr[period] = tr[1:period+1].mean()
        for i in range(period+1, n):
            atr[i] = (atr[i-1]*(period-1) + tr[i]) / period
    hl2 = (hi + lo) / 2.0
    up = hl2 + mult * atr
    dn = hl2 - mult * atr
    sig = np.zeros(n)
    for i in range(1, n):
        if atr[i] == 0:
            sig[i] = sig[i-1]; continue
        dn[i] = max(dn[i], dn[i-1]) if cl[i-1] >= dn[i-1] else dn[i]
        up[i] = min(up[i], up[i-1]) if cl[i-1] <= up[i-1] else up[i]
        sig[i] = 1 if cl[i] > up[i] else (-1 if cl[i] < dn[i] else sig[i-1])
    return sig


def _rank_score(a: dict) -> float:
    """core/sniper_engine.py::_rank_score_single_st_1h."""
    bucket_score = 100 if a["bars_since_flip"] <= APPENA_MAX_BARS else 50
    rs_score = max(min(a["rs_pct"] * a["dir_int"] * 1.5, 15.0), 0.0)
    vol_score = max(min((a["spike"] - 10.0) / 90.0, 1.0), 0.0) * 10.0
    return bucket_score + rs_score + vol_score


def _is_in_trend_leader(a: dict) -> bool:
    """core/sniper_engine.py::_is_in_trend_leader."""
    return (a["tf_1d_aligned"] is True and a["dir_int"] != 0
            and a["rs_pct"] * a["dir_int"] >= IN_TREND_RS_MIN_PCT
            and a["spike"] >= IN_TREND_VOL_MIN_PCT)


def _features(df: pd.DataFrame, btc_ret: pd.Series) -> pd.DataFrame:
    """Per ogni barra 4H chiusa: cio' che scan_single_st_1h vedrebbe subito dopo la chiusura."""
    cl = df["close"].values.astype(np.float64)
    hi = df["high"].values.astype(np.float64)
    lo = df["low"].values.astype(np.float64)
    vol = df["volume"].values.astype(np.float64)
    sig = _supertrend(cl, hi, lo, ST_PERIOD, ST_MULT)

    # bars_since_flip: barre consecutive in coda con sig == dir_now, barra corrente inclusa
    bsf = np.zeros(len(sig), dtype=int)
    for i in range(len(sig)):
        bsf[i] = bsf[i-1] + 1 if i > 0 and sig[i] == sig[i-1] else 1

    # _rs_1bar: (ret asset - ret BTC) * 100 sull'ultima barra chiusa
    ret = pd.Series(cl, index=df.index).pct_change()
    rs = ((ret - btc_ret.reindex(df.index)) * 100.0).fillna(0.0).values
    rs[0] = 0.0

    # spike: % sopra la media delle 40 barre precedenti, corrente esclusa (len > 41)
    v = pd.Series(vol, index=df.index)
    avg = v.shift(1).rolling(40).mean()
    spike = ((v / avg - 1.0) * 100.0).where(avg > 0).fillna(0.0).values
    spike[:41] = 0.0

    # ST 1D sulle candele giornaliere CHIUSE al momento della chiusura della barra 4H
    d1 = df[["open", "high", "low", "close"]].resample("1D", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    sig1d = pd.Series(_supertrend(d1["close"].values, d1["high"].values, d1["low"].values,
                                  ST_PERIOD, ST_MULT), index=d1.index)
    n1d_closed = pd.Series(np.arange(1, len(d1) + 1), index=d1.index)
    bar_close = df.index + pd.Timedelta(hours=4)
    last_closed_day = bar_close.floor("1D") - pd.Timedelta(days=1)
    dir1d = sig1d.reindex(last_closed_day, method="ffill").values
    cnt1d = n1d_closed.reindex(last_closed_day, method="ffill").fillna(0).values

    exit_dir = _daily_forming_dir(df, d1)

    return pd.DataFrame({
        "dir_int": sig.astype(int), "bars_since_flip": bsf, "rs_pct": rs, "spike": spike,
        "n4h": np.arange(1, len(df) + 1), "dir1d": np.nan_to_num(dir1d), "n1d": cnt1d,
        "exit_dir": exit_dir,
    }, index=df.index)


def _supertrend_state(cl, hi, lo, period, mult):
    """Come _supertrend, ma restituisce anche atr, up e dn finali di ogni barra."""
    n = len(cl)
    tr = np.zeros(n)
    for i in range(1, n):
        tr[i] = max(hi[i]-lo[i], abs(hi[i]-cl[i-1]), abs(lo[i]-cl[i-1]))
    atr = np.zeros(n)
    if n > period:
        atr[period] = tr[1:period+1].mean()
        for i in range(period+1, n):
            atr[i] = (atr[i-1]*(period-1) + tr[i]) / period
    hl2 = (hi + lo) / 2.0
    up = hl2 + mult * atr
    dn = hl2 - mult * atr
    sig = np.zeros(n)
    for i in range(1, n):
        if atr[i] == 0:
            sig[i] = sig[i-1]; continue
        dn[i] = max(dn[i], dn[i-1]) if cl[i-1] >= dn[i-1] else dn[i]
        up[i] = min(up[i], up[i-1]) if cl[i-1] <= up[i-1] else up[i]
        sig[i] = 1 if cl[i] > up[i] else (-1 if cl[i] < dn[i] else sig[i-1])
    return atr, up, dn, sig


def _daily_forming_dir(df: pd.DataFrame, d1: pd.DataFrame) -> np.ndarray:
    """Direzione del ST(6,2) giornaliero sulla candela IN FORMAZIONE, alla chiusura di ogni barra 4H.

    Ultimo elemento di _supertrend(giorni chiusi + candela parziale): un passo della ricorsione
    dallo stato dell'ultimo giorno chiuso. 0 = non disponibile (la produzione tiene la posizione).
    """
    dc, dh, dl = (d1[k].values.astype(np.float64) for k in ("close", "high", "low"))
    atr_d, up_d, dn_d, sig_d = _supertrend_state(dc, dh, dl, ST_PERIOD, ST_MULT)
    day_pos = {ts: i for i, ts in enumerate(d1.index)}
    day = df.index.floor("1D")
    g = pd.Series(df["open"].values, index=df.index).groupby(day)
    o_day = g.transform("first").values
    h_day = pd.Series(df["high"].values, index=df.index).groupby(day).cummax().values
    l_day = pd.Series(df["low"].values, index=df.index).groupby(day).cummin().values
    c_now = df["close"].values.astype(np.float64)
    out = np.zeros(len(df))
    for j in range(len(df)):
        k = day_pos.get(day[j], 0) - 1          # ultimo giorno chiuso
        if k < ST_PERIOD or atr_d[k] == 0:
            continue
        h, l, c, pc = h_day[j], l_day[j], c_now[j], dc[k]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        atr = (atr_d[k] * (ST_PERIOD - 1) + tr) / ST_PERIOD
        hl2 = (h + l) / 2.0
        up = hl2 + ST_MULT * atr
        dn = hl2 - ST_MULT * atr
        dn = max(dn, dn_d[k]) if pc >= dn_d[k] else dn
        up = min(up, up_d[k]) if pc <= up_d[k] else up
        out[j] = 1 if c > up else (-1 if c < dn else sig_d[k])
    return out


class SignalEngine:
    def __init__(self):
        self.trades_log: list = []

    def generate(self, data_map: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        codes = [f"{t}-USDT-PERP" for t in UNIVERSE if f"{t}-USDT-PERP" in data_map]
        frames = {c: data_map[c].sort_index() for c in codes}
        btc_ret = frames[BTC_CODE]["close"].pct_change() if BTC_CODE in frames else pd.Series(dtype=float)
        feats = {c: _features(frames[c], btc_ret) for c in codes}

        timeline = sorted(set().union(*[f.index for f in feats.values()]))
        feat_rows = {c: feats[c].to_dict("index") for c in codes}
        pos_of = {c: {ts: i for i, ts in enumerate(frames[c].index)} for c in codes}
        w_arr = {c: np.zeros(len(frames[c])) for c in codes}
        held: Dict[str, int] = {}   # code -> direzione (+1 / -1)
        sim_start = pd.Timestamp(SIM_START)

        for t in timeline:
            if t < sim_start:
                continue
            rows = {c: feat_rows[c][t] for c in codes if t in feat_rows[c]}

            # 1. Uscite: ST giornaliero in formazione opposto alla posizione
            #    (asset_strategy.evaluate, live_exit=True; segnale 0 -> si tiene)
            for c in list(held):
                if c in rows:
                    ed = int(rows[c]["exit_dir"])
                    if ed in (1, -1) and ed != held[c]:
                        del held[c]

            # 2. Rescan e riempimento (portfolio_5slot.rescan_and_fill)
            free = N_MAX_SLOTS - len(held)
            if free > 0:
                assets_all = []
                for c in codes:   # ordine dell'universo = ordine dello scan
                    r = rows.get(c)
                    if r is None or r["n4h"] < MIN_4H_BARS or int(r["dir_int"]) == 0:
                        continue
                    aligned = (int(r["dir1d"]) == int(r["dir_int"])) if r["n1d"] >= MIN_1D_CLOSED else None
                    assets_all.append({
                        "code": c, "dir_int": int(r["dir_int"]),
                        "bars_since_flip": int(r["bars_since_flip"]),
                        "rs_pct": round(float(r["rs_pct"]), 2), "spike": round(float(r["spike"]), 1),
                        "tf_1d_aligned": aligned,
                    })
                by_bsf = lambda x: x["bars_since_flip"]
                appena = sorted([a for a in assets_all if a["bars_since_flip"] <= APPENA_MAX_BARS], key=by_bsf)
                confermati = sorted([a for a in assets_all
                                     if APPENA_MAX_BARS < a["bars_since_flip"] <= CONFERMATI_MAX_BARS], key=by_bsf)
                in_trend = sorted([a for a in assets_all if a["bars_since_flip"] > CONFERMATI_MAX_BARS], key=by_bsf)

                fresh = [a for a in appena + confermati if a["code"] not in held and a["tf_1d_aligned"] is True]
                ranked = sorted(fresh, key=_rank_score, reverse=True)
                free_needed = max(0, free - len(ranked))
                if free_needed:
                    leaders = [a for a in in_trend if a["code"] not in held and _is_in_trend_leader(a)]
                    ranked.extend(sorted(leaders, key=_rank_score, reverse=True)[:free_needed])
                for a in ranked[:free]:
                    held[a["code"]] = a["dir_int"]

            for c, d in held.items():
                if c in rows:
                    w_arr[c][pos_of[c][t]] = SLOT_SIZE * d

        # Asset senza barra a t (gap/delisting): il peso resta quello dell'ultima barra
        return {c: pd.Series(w_arr[c], index=frames[c].index) for c in codes}
