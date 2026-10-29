# Fase 2A — Calibrazione strategy_engine contro Vibe-Trading: resoconto

Data: 29/10/2026 · Modalità: validazione · Pre-registrazione: `research/preregistration/2026-10-29_fase2A_calibrazione_motori.md` (con errata)

## Esito in una riga

I due motori sono **calibrati**: con le stesse regole contabili lo scarto massimo è **0,086 punti percentuali** su 6 fold.
Il confronto pre-registrato invece **non rientra nelle tolleranze** (mediana 2,90 pp, massimo 7,80 pp sul sizing tier),
e la causa di ogni punto di differenza è stata trovata riga per riga, come richiesto dalla sezione 6.

## Metodo

1. `registratore.py`: importa `sweep_may_vs_fixed.py` senza modificarlo, intercetta `apply_exit` e `run_portfolio`
   e salva, per la variante A di ogni fold, gli input esatti (open, high, low, close, funding, validità, momentum,
   segnali) e il risultato del motore di ricerca. Totali identici alla riproduzione: tier 937,7%, equal 195,5%.
2. Fedeltà della cattura: `run_portfolio` rieseguito sugli input catturati ridà il risultato salvato in **12 casi su 12**.
3. `confronto_motori.py`: stessi input in Vibe-Trading 0.1.18, una run per fold, commissione 0,05% per lato,
   slippage 0, senza funding (vedi punto D). Peso obiettivo della barra i+1 passato sulla barra i, perché
   Vibe-Trading esegue all'open della barra dopo il segnale.

## Confronto pre-registrato (sizing tier, senza funding)

| Fold | Ricerca | Vibe-Trading | Diff (pp) | Trade ricerca | Trade Vibe |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 139,13% | 134,97% | −4,16 | 300 | 300 |
| 1 | 59,65% | 67,45% | +7,80 | 398 | 398 |
| 2 | 91,12% | 88,25% | −2,86 | 373 | 373 |
| 3 | −19,57% | −20,22% | −0,66 | 428 | 428 |
| 4 | 48,85% | 51,09% | +2,24 | 394 | 394 |
| 5 | 19,24% | 22,17% | +2,93 | 418 | 418 |

Criterio 1 (trade ±2%): **rispettato**, identici. Criterio 2 (mediana ≤ 1,0 pp, max ≤ 3,0 pp): **non rispettato**.
Sul fold 1, i 398 ingressi coincidono tutti per barra, asset e prezzo: cambia solo la quantità.

## Le cause (tutte nel motore di ricerca, `research/sweep_may_vs_fixed.py`)

**A. Equity valutata alla chiusura della barra in cui si compra** (`run_portfolio`, riga `eq_now=...['cl'][i]...`).
L'ordine si esegue all'open della barra i ma si dimensiona con il close della stessa barra, non ancora noto: è un
look-ahead. Effetto sul rendimento per fold: fino a 1,6 pp. Vibe-Trading valuta all'open (`base.py:1245`,
commento esplicito sul motivo).

**B. Leva implicita nel sizing tier.** Le posizioni già aperte non vengono mai ridimensionate e il nuovo entrato
prende il peso del suo rango attuale: l'esposizione lorda supera il 100% dell'equity nell'**11,1% delle barre**
(727 su 6.570), con massimo 131,7%. La regola dichiarata "40/30/20" (90%) non è quella eseguita. Vibe-Trading con
leva 1 riduce gli ordini alla liquidità disponibile, senza segnalarlo (0 rifiuti registrati). Effetto: fino a 7,5 pp.

**C. Sizing equal senza tetto.** 9,5% a ogni asset attivo: esposizione oltre il 100% in quasi tutte le barre
(per esempio 1.103 su 1.104 nel fold 0). Vibe-Trading normalizza i pesi a somma ≤ 1: il confronto equal non è
significativo con questa regola, e non lo si usa per la calibrazione.

**D. Funding assente in 5 fold su 6** (`get_daily_funding`, righe 87-104). La prima richiesta senza `startTime`
restituisce circa 500 regolamenti; `if len(data)<1000: break` la scambia per l'ultima pagina. Prova: per BTC
chiesti 1.500 giorni, ricevuti 167 (16/05/2026 → 29/10/2026). In più il funding si scarica sempre da oggi
all'indietro e ignora `--asof`: la baseline "congelata" cambia con la data in cui si esegue.
Barre con funding ≠ 0: fold 0-4 = 0%; fold 5 = 44,2%.

## Prova della calibrazione

Replica della logica di ricerca con le regole contabili di Vibe-Trading (equity all'open prima delle chiusure, poi
chiusure, poi aperture), contro Vibe-Trading con leva 2 e pesi dimezzati (stesso nozionale, margine sufficiente):

| Fold | Replica | Vibe-Trading | Scarto (pp) |
| --- | ---: | ---: | ---: |
| 0 | 138,4679% | 138,3814% | −0,086 |
| 1 | 59,9623% | 59,9126% | −0,050 |
| 2 | 89,4885% | 89,4078% | −0,081 |
| 3 | −20,6401% | −20,6777% | −0,038 |
| 4 | 49,4833% | 49,4166% | −0,067 |
| 5 | 18,4037% | 18,3465% | −0,057 |

## Conseguenze

- Vibe-Trading è utilizzabile come secondo motore: dà gli stessi numeri a parità di regole.
- I risultati del motore di ricerca con sizing tier o equal contengono leva non dichiarata (B, C), un piccolo
  look-ahead nel sizing (A) e quasi nessun funding (D). Le correzioni proposte (non applicate) vanno decise
  dall'utente prima di usare quei numeri: equity all'open; normalizzazione dei pesi o leva dichiarata;
  paginazione del funding per `startTime` con `asof`.
