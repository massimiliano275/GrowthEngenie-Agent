# Pre-registrazione — Fase 2A: calibrazione strategy_engine contro Vibe-Trading

| Campo | Valore |
| --- | --- |
| Data di registrazione | 2026-10-29 |
| Autore | Claude Code, su richiesta di Massimiliano |
| Oggetto | i due motori, non la strategia |
| Codice di riferimento | `growthengenie3st_backpack/research/sweep_may_vs_fixed.py`, `walk_forward_variants(..., exits=True)`, variante d'uscita **A**; commit della repo locale al 29/10/2026 (branch `master`) |
| Motore 2 | vibe-trading-ai 0.1.18 |

## 1. Ipotesi

Con la **stessa logica**, gli **stessi dati** e gli **stessi costi**, Vibe-Trading riproduce i risultati di `sweep_may_vs_fixed.py`
entro le tolleranze della sezione 6. Ogni differenza oltre tolleranza ha una causa identificabile nel codice di uno dei due motori.

## 2. Logica da tradurre fedelmente (non è la produzione)

- Comando di riferimento: `python research/sweep_may_vs_fixed.py --wf_exits --asof 2026-10-01` (default: `--tf 1d`, `--mom 30`, `--slot_frac 0.095`, `--universe_n 14`, `--pool_size 40`).
- Trigger: `st_direction(6, 2.0)` del motore di ricerca, **ATR esponenziale** `alpha = 2/(p+1)` (non quello di produzione).
- Pool: 40 perp USDT con più volume negli ultimi 30 giorni alla data `asof`.
- Fold walk-forward: train e test come da default dello script; a ogni fold il paniere è formato dai 14 asset con più volume medio nel train.
- Segnale spostato di 1 barra, esecuzione all'apertura; uscita solo sul flip (variante A).
- Dimensione **tier**: a ogni barra i 3 asset attivi con `direzione × momentum(30)` più alto, al 40/30/20% dell'equity.
- Dimensione **equal**: 9,5% dell'equity a ogni asset attivo, senza tetto.
- Ogni fold riparte da capitale 1.000 e posizioni nulle; il risultato totale è il prodotto dei rendimenti dei fold.

## 3. Dati e periodo

- Gli **stessi** dati scaricati dallo script con `--asof 2026-10-01` (klines Binance USD-M e funding giornaliero), salvati su file e passati a Vibe-Trading come sorgente locale. Nessun nuovo download per il motore 2.
- Prova d'identità dei dati: la riga `[diag] fingerprint BTC` dello script (attesa: n=9000, somma_cl=564666046.2, ultimo 2026-09-30 20:00 UTC, come in `PROMPT_RIPRESA.md`).

## 4. Costi

- Commissione 0,05% per lato su entrambi i motori; slippage 0.
- Funding: come nello script (tasso giornaliero diviso per barre del giorno, applicato sul close); in Vibe-Trading lo stesso tasso, fornito come colonna.

## 5. Metriche

- Per fold: rendimento tier ed equal (%); numero di trade.
- Totale cucito: prodotto dei rendimenti dei fold, tier ed equal.

## 6. Criteri

Calibrati se **tutte** valgono:
1. numero di trade per fold uguale entro ±2%;
2. differenza di rendimento per fold: mediana ≤ 1,0 punto percentuale, massima ≤ 3,0 punti;
3. totale cucito tier ed equal: differenza relativa ≤ 5%.

Non calibrati altrimenti: si cerca la causa riga per riga prima di qualsiasi altro uso dei due motori.

Differenze strutturali note, da quantificare e non da correggere:
- Vibe-Trading esegue un portafoglio continuo; lo script riparte da zero a ogni fold (una commissione d'ingresso in più per posizione e per fold).
- Vibe-Trading ribilancia solo quando cambia il peso obiettivo; lo script ricalcola i pesi tier a ogni barra.

## Errata (29/10/2026, prima di qualsiasi risultato del walk-forward)

Il comando della sezione 2 era incompleto: senza `--wf_filters` lo script esegue l'esperimento di default
(config di maggio, finestra fino a oggi, `--asof` ignorato). La baseline di `PROMPT_RIPRESA.md` è a 4H
(impronta BTC n=9000 = 1500 giorni × 6 barre). Comando corretto, unico ammesso:

    python research/sweep_may_vs_fixed.py --wf_filters --wf_exits --tf 4h --asof 2026-10-01

Default che restano: `--wf_train 12`, `--wf_test 6`, `--mom 30` (giorni → 180 barre 4H), `--slot_frac 0.095`,
`--universe_n 14`, `--pool_size 40`, `--history 1500`. Nessun altro criterio cambia.

## 7. Cosa NON si farà

- Nessuna modifica a `sweep_may_vs_fixed.py` né al motore di Vibe-Trading durante la calibrazione.
- Nessun giudizio sulla strategia: qui si misurano i motori.
- La divergenza tra ATR esponenziale (ricerca) e ATR di Wilder (produzione) si documenta a parte; non si corregge qui.
