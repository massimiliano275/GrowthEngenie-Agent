"""Lancia il runner di Vibe-Trading tollerando i BORDI DI QUOTAZIONE dei perp Binance.

vibe-trading-ai 0.1.18, backtest/loaders/ccxt_loader.py::_fetch_perpetual fallisce per
l'intero universo appena un perp e' quotato dentro la finestra:
  - "funding settlement data is missing": la prima barra precede il primo funding
    (HYPE: barra 2025-05-30 08:00, primo funding 12:00)
  - "mark-price timestamps are incomplete or unsynchronized": le klines di trade e di
    mark non iniziano sulla stessa barra (PENGU)

Questa versione rifa' la stessa costruzione (trade + mark + funding) con due sole tolleranze:
  1. si tengono le barre presenti sia nel trade sia nel mark; le scartate vengono stampate
  2. prima del primo funding reale il tasso e' 0 (prima della quotazione non si paga funding)
Dopo il primo funding reale un regolamento mancante continua a fermare il run.

Uso: python run_backtest_listing_safe.py <run_dir>
"""
import sys
from pathlib import Path

import pandas as pd

from backtest.loaders import ccxt_loader as L

_report = []
_delisted = []
_non_quotati = []


def _fetch_perpetual(cls, exchange, symbol, timeframe, since_ms, end_ms,
                     bracket_artifact=None, require_brackets=False):
    if require_brackets and bracket_artifact is None:
        raise ValueError(f"strict margin-risk fetch for {symbol} requires a maintenance-bracket artifact")
    trade = cls._fetch_one(exchange, symbol, timeframe, since_ms, end_ms)
    mark = cls._fetch_one(exchange, symbol, timeframe, since_ms, end_ms, params={"price": "mark"})
    if trade is None and mark is None:
        # asset non ancora quotato (o gia' rimosso) in tutto il periodo: nessun dato, escluso
        # dall'universo come fa la produzione quando le klines non arrivano
        _non_quotati.append(symbol)
        return pd.DataFrame()
    if trade is None or mark is None:
        raise ValueError(f"mark-price or trade candles missing for {symbol}")
    common = trade.index.intersection(mark.index)
    dropped_t, dropped_m = len(trade.index) - len(common), len(mark.index) - len(common)
    trade, mark = trade.loc[common], mark.loc[common]

    # 3. Perp delistato (status != TRADING): barre solo fino alla data di consegna
    info = exchange.market(symbol).get("info", {})
    if info.get("status") != "TRADING" and info.get("deliveryDate"):
        delivery = pd.Timestamp(int(info["deliveryDate"]), unit="ms")
        keep = trade.index < delivery.floor("4h")
        if not keep.all():
            _delisted.append((symbol, info.get("status"), str(delivery), int((~keep).sum())))
            trade, mark = trade.loc[keep], mark.loc[keep]
            end_ms = min(end_ms, int(delivery.timestamp() * 1000))

    result = trade.copy()
    result["execution_open"] = trade["open"]
    for column in ("open", "high", "low", "close"):
        result[f"mark_{column}"] = mark[column]

    funding = cls._fetch_funding_history(exchange, symbol, since_ms, end_ms)
    if funding.index.has_duplicates:
        raise ValueError(f"duplicate funding settlement for {symbol}")
    first_real = funding.index.min() if not funding.empty else None
    required = result.index[result.index.hour.isin(L._FUNDING_HOURS)]
    if first_real is not None:
        required = required[required >= first_real]
    missing = required.difference(funding.index)
    if not missing.empty:
        raise ValueError(f"funding settlement data is missing for {symbol}: "
                         f"{', '.join(str(ts) for ts in missing[:10])}")

    result["funding_rate"] = 0.0
    result["funding_settlement_time"] = pd.NaT
    aligned = funding.index.intersection(result.index)
    if not aligned.empty:
        result.loc[aligned, "funding_rate"] = funding.loc[aligned, "funding_rate"]
        result.loc[aligned, "funding_settlement_time"] = aligned
    # Barre prima del primo funding reale: regolamento a tasso 0 alle ore di funding
    if first_real is not None:
        pre = result.index[(result.index < first_real) & result.index.hour.isin(L._FUNDING_HOURS)]
        result.loc[pre, "funding_settlement_time"] = pre
    else:
        pre = result.index[result.index.hour.isin(L._FUNDING_HOURS)]
        result.loc[pre, "funding_settlement_time"] = pre

    _report.append((symbol, len(result), dropped_t, dropped_m, len(pre) if first_real is not None else -1,
                    str(result.index.min()) if len(result) else "-"))
    if bracket_artifact is not None:
        raise ValueError("bracket artifacts non supportati da questo lanciatore")
    return result


L.DataLoader._fetch_perpetual = classmethod(_fetch_perpetual)

# Cache su disco del frame finale (trade + mark + funding) per simbolo, timeframe e intervallo:
# le run in serie e in parallelo rileggono il file invece di riscaricare (Binance: 429 oltre 2400 req/min).
import hashlib
import os

_CACHE_DIR = Path(os.environ.get("LISTING_SAFE_CACHE", Path(__file__).resolve().parent.parent / "data_cache"))
_fetch_perpetual_rete = L.DataLoader._fetch_perpetual


def _fetch_perpetual_cache(cls, exchange, symbol, timeframe, since_ms, end_ms,
                           bracket_artifact=None, require_brackets=False):
    key = hashlib.sha1(f"{symbol}|{timeframe}|{since_ms}|{end_ms}".encode()).hexdigest()[:16]
    f = _CACHE_DIR / f"{symbol.replace('/', '_').replace(':', '_')}_{timeframe}_{key}.pkl"
    if f.exists():
        _report_cache["letti"] += 1
        return pd.read_pickle(f)
    df = _fetch_perpetual_rete.__func__(cls, exchange, symbol, timeframe, since_ms, end_ms,
                                        bracket_artifact=bracket_artifact, require_brackets=require_brackets)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    df.to_pickle(tmp)
    tmp.replace(f)
    _report_cache["scaricati"] += 1
    return df


_report_cache = {"letti": 0, "scaricati": 0}
L.DataLoader._fetch_perpetual = classmethod(_fetch_perpetual_cache)

from backtest import runner  # noqa: E402

try:
    runner.main(Path(sys.argv[1]))
finally:
    print("\n[bordi quotazione] simbolo | barre | scartate trade | scartate mark | funding a 0 | prima barra")
    for row in _report:
        if row[2] or row[3] or row[4]:
            print("[bordi quotazione]", " | ".join(str(x) for x in row))
    for row in _delisted:
        print("[delisting] simbolo | status | consegna | barre tolte:", " | ".join(str(x) for x in row))
    print(f"[cache] letti {_report_cache['letti']} | scaricati {_report_cache['scaricati']}")
    if _non_quotati:
        print(f"[non quotati nel periodo] {len(_non_quotati)}: {' '.join(_non_quotati)}")
