# Fase 0 — Look-ahead: resoconto di chiusura

Data: 29/10/2026 · Modalità: validazione · Nessun codice modificato.

Prova eseguibile: `test_fase0_lookahead.py` (accanto a questo file). Oggi i due test **falliscono**:
è la prova che i problemi esistono. Devono passare dopo le correzioni proposte.

```
python -m pytest test_fase0_lookahead.py -v
```

## A. Phoenix — lato delle barre ambigue

| Voce | Valore |
| --- | --- |
| File e righe | `growthengenie3st_backpack/phoenix/backtest.py`, 394-399 |
| Categoria | (b) codice della strategia |
| Input | riferimento H 110, L 100; barra successiva O 105, H 112, L 98, chiusura 111 oppure 99 |
| Atteso | stesso lato e stesso prezzo d'ingresso: tutto ciò che si sapeva al primo tocco è identico |
| Ottenuto | chiusura 111 → LONG a 110; chiusura 99 → SHORT a 100 |
| Causa | se la barra tocca entrambi i livelli, il lato si sceglie con `Close[i] >= Open[i]`, ignota al momento del primo tocco |
| Peso storico | 8 barre ambigue su BTC 1D 2017-08-17 → 2026-10-24 |

Correzione proposta (non applicata): parametro `ambiguous_policy` in `BacktestConfig`.

| Valore | Comportamento |
| --- | --- |
| `minute` | ordine dei tocchi dai dati a 1 minuto; esatto, da usare nella Fase 3 |
| `worst` | si prende il lato che dà il risultato peggiore; limite prudente senza dati a 1 minuto |
| `skip` | nessun ingresso sulle barre ambigue |
| `close_vs_open` | regola attuale, solo per riprodurre i vecchi numeri, marcata come look-ahead |

Test: `test_a_phoenix_barra_ambigua_non_dipende_dalla_chiusura`.
Dove si applica: nella chat dedicata a Phoenix.

Nota separata (non è look-ahead): lo short è calcolato come `entry/exit - 1` (righe 431, 461, 499, 586);
su un perp lineare è `(entry - exit)/entry`. Short 100 → 50: +100% invece di +50%.

## B. Vibe-Trading — `factor_analysis` non sposta le date

| Voce | Valore |
| --- | --- |
| File e righe | `site-packages/src/factors/factor_analysis_core.py`, `compute_ic_series`, 22-41 (vibe-trading-ai 0.1.18) |
| Categoria | (d) non è un look-ahead del motore: lo strumento accetta senza avviso un input con look-ahead |
| Input | fattore uguale ai rendimenti dello stesso giorno (test); forza relativa a 1 giorno su 64 perp con rendimenti dello stesso giorno (caso reale) |
| Atteso | errore o avviso |
| Ottenuto | `status: ok`, IC 1,000 (caso reale: IR 5,1e15, spread 2,4e18) |
| Con allineamento corretto | IC -0,019 sui 64 perp |

Correzione proposta (non applicata):
1. parametro obbligatorio `returns_alignment`: `forward` (rendimenti già futuri) oppure `same_day`
   (lo strumento li sposta in avanti di `horizon` barre);
2. controllo: `status: "suspect_lookahead"` se |IC medio| > 0,9.

Test: `test_b_factor_analysis_segnala_allineamento_stesso_giorno`.
Issue per la repo ufficiale: da preparare dopo verifica sull'ultima versione, invio solo con ok.

## Motore di backtest di Vibe-Trading — controllo negativo

`backtest/engines/base.py`, `_align`: i segnali sono spostati di una barra (esecuzione all'apertura
successiva). Nessun look-ahead trovato.

## Esito

Fase 0 chiusa: due look-ahead provati, nessuno nel motore di backtest di Vibe-Trading.
La validazione delle strategie può procedere, con queste due avvertenze attive:
Phoenix va simulato con `minute` (o `worst`), e `factor_analysis` si usa solo con rendimenti futuri allineati a mano.
