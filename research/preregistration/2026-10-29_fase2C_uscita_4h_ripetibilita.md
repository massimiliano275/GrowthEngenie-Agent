# Pre-registrazione — Fase 2C: ingressi e uscite a 4H (conferma 1D sugli ingressi), ripetibilità

| Campo | Valore |
| --- | --- |
| Data di registrazione | 2026-10-29 |
| Autore | Claude Code, su richiesta di Massimiliano ("ingressi e uscite a 4H, conferma 1D per gli ingressi") |
| Motore | Vibe-Trading 0.1.18, calibrato in Fase 2A |
| Codice | traduzione del 25/10 (`vibe_trading/runs/backpack_4h/code/signal_engine.py`, fedeltà dello scan 100%), con tre costanti: `N_MAX_SLOTS`, `SLOT_SIZE`, `SIM_START` |

## 1. Ipotesi

Con uscita sul flip del SuperTrend 4H, invece del giornaliero in formazione (Fase 2B), le posizioni durano meno,
gli slot si liberano più spesso e la strategia cattura i movimenti eccezionali in modo più ripetibile anche a 5 slot.

## 2. Regole

- Scan e ingresso: identici alla Fase 2B (flip ST(6, 2,0) 4H fresco ≤ 3 barre, conferma ST 1D sull'ultima candela
  chiusa, punteggio bucket + RS + volume, leader in trend se restano slot vuoti), esecuzione all'open 4H successivo.
- **Uscita**: flip del ST(6, 2,0) **4H a candela chiusa** opposto alla posizione, esecuzione all'open successivo.
  Limite dichiarato: se in produzione si impostasse `TIMEFRAME "4h"`, `live_exit` userebbe la candela 4H in
  formazione, valutata ogni minuto; il simulatore usa la candela chiusa.
- Configurazioni: **5 slot × 19%** (scelta dell'utente) e **10 slot × 9,5%** (riferimento).

## 3. Dati, periodo, partenze

- 64 perp Binance USD-M, dati 4H dal 01/05/2024, fine il 30/09/2026; lanciatore `run_backtest_listing_safe.py`.
- **26 date di partenza** a slot vuoti, ogni 14 giorni: dal 01/07/2024 al 16/06/2025 compreso
  (01/07/2024 + k × 14 giorni, k = 0…25). Ogni run va dalla sua partenza al 30/09/2026.
- 2 configurazioni × 26 partenze = 52 run.

## 4. Costi

Commissione 0,05% per lato, slippage 0,05% per lato, funding storico Binance (non strict). Come in Fase 2B.

## 5. Metriche

Per ogni run: rendimento totale, rendimento annuo dalla partenza, drawdown massimo, Sharpe, operazioni,
durata media, numero di operazioni chiuse con rendimento ≥ +100% ("catture eccezionali").

Aggregate per configurazione: mediana, 25° e 75° percentile, minimo e massimo di rendimento annuo e drawdown;
quota di partenze con rendimento positivo; quota di partenze in cui 5 slot batte 10 slot; numero medio di catture
eccezionali; quota di partenze che catturano il long ZEC di fine 2025.

Confronto con la Fase 2B solo sulla partenza del 01/07/2024 (unica in comune).

## 6. Criteri

Misura descrittiva, nessuna promozione automatica. La decisione resta all'utente. Si dichiarano in anticipo
le letture:
- "5 slot regge" se la mediana del rendimento annuo a 5 slot è ≥ quella a 10 slot − 5 punti e il drawdown
  mediano a 5 slot non è peggiore di quello a 10 slot di oltre 10 punti;
- "uscita 4H migliore della giornaliera" si legge solo sulla partenza comune del 01/07/2024 (limite: una storia).

Controlli: meccanica (posizioni ≤ N, pesi solo ±SLOT_SIZE, commissioni 5 bp) su almeno una run per configurazione.

## 7. Cosa NON si farà

- Nessun'altra configurazione di slot, peso, uscita o soglia.
- Nessuna scelta della data di partenza "migliore": le 26 partenze si leggono tutte insieme.
- Nessuna modifica alla produzione in questa fase.
