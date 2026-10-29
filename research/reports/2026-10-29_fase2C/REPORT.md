# Fase 2C — Uscita a 4H, 5 contro 10 slot, 26 partenze (resoconto)

Data: 29/10/2026 · Modalità: validazione · Pre-registrazione: `research/preregistration/2026-10-29_fase2C_uscita_4h_ripetibilita.md`

## Esito in tre righe

- Con uscita sul flip 4H, **10 slot × 9,5% fa meglio di 5 slot × 19% in 26 partenze su 26**: rendimento annuo
  mediano +27,8% contro −8,0%, drawdown −40,0% contro −62,0%. La lettura pre-registrata "5 slot regge" è **falsa**.
- L'uscita a 4H accorcia le posizioni da circa 100 giorni (uscita giornaliera, Fase 2B) a circa 24.
- **Limite che ridimensiona il test**: le run convergono alle **stesse posizioni** entro 1-10 giorni dalla partenza.
  Le 26 partenze sono la stessa storia vista da giorni diversi, non 26 storie indipendenti.

## Controlli

| Controllo | Esito |
| --- | --- |
| Run completate | 52 su 52, 0 errori (dopo la correzione della cache, sotto) |
| Posizioni massime | 5 e 10, mai superate |
| Regressione | partenza 01/07/2024 a 10 slot = +147,17%, identica alla run del 25/10; identica anche rieseguita dalla cache |

## Risultati

| Metrica | 5 slot × 19% | 10 slot × 9,5% |
| --- | ---: | ---: |
| Rendimento annuo, mediana [25° / 75°] | −8,0% [−16,4 / −1,5] | +27,8% [+18,7 / +42,5] |
| Rendimento annuo, min / max | −30,2% / +7,6% | +2,3% / +60,4% |
| Rendimento totale, mediana | −14,8% | +50,9% |
| Drawdown massimo (tutte le partenze) | −62,0% | −40,0% |
| Sharpe, mediana [min / max] | 0,21 [−0,26 / 0,45] | 0,72 [0,30 / 1,08] |
| Partenze in guadagno | 5 su 26 | 26 su 26 |
| Catture ≥ +100%, media [min / max] | 1,88 [1 / 3] | 3,50 [1 / 6] |
| Long ZEC di fine 2025 catturato | 26 su 26 | 26 su 26 |
| Durata media delle posizioni | 23,3 giorni | 24,1 giorni |
| 5 slot batte 10 slot | 0 partenze su 26 | — |

Drawdown massimo, identico in ogni partenza perché le storie convergono: a 5 slot dal picco del 12/10/2025 al
fondo del 04/05/2026 (−62,0%); a 10 slot dall'11/10/2025 al 17/08/2026 (−40,0%).

Sulla partenza comune con la Fase 2B (01/07/2024): uscita giornaliera 5 slot −67,9% → uscita 4H +13,5%;
10 slot +70,0% → +147,2%. Una sola storia.

## Il limite: convergenza delle partenze

Posizioni identiche a quelle della partenza 01/07/2024: partenza 15/07/2024 dal 28/07 (5 slot) e dal 24/07
(10 slot); 04/11/2024 dal 06/11; 10/02/2025 dall'11/02 e dal 20/02; 16/06/2025 dal 23/06. Con uscite rapide il
portafoglio dimentica il punto di partenza in pochi giorni. La "distribuzione" sulle 26 partenze misura quindi
**da quale giorno si entra nella stessa curva**, non la ripetibilità della strategia.

Conseguenza: il confronto 5 contro 10 è affidabile come confronto **su questa storia** (0 su 26 a favore di 5),
ma resta una sola storia di mercato (luglio 2024 → settembre 2026).

## Alternative concrete per una ripetibilità vera

1. **Periodo mai usato**: stessa strategia e stessi parametri su gennaio 2021 → giugno 2024 (perp Binance
   disponibili), pre-registrato. È l'unica replica su dati davvero nuovi.
2. **Universi casuali**: 30 sottoinsiemi casuali di 40 asset sui 64, stesse regole: misura quanto il risultato
   dipende da quali asset sono nell'universo (fortuna della selezione).

## Incidente durante il batch (risolto)

La prima esecuzione parallela ha superato il limite di Binance (2.400 richieste al minuto per IP, errore 429):
il lanciatore riscaricava i dati a ogni run. Aggiunta una cache su disco in `run_backtest_listing_safe.py`
(stesso frame del loader, salvato una volta); prova di regressione superata (+147,17% identico, 37 s per run
invece di circa 5 minuti). Il bot di produzione non è stato toccato (gira su un altro IP).
