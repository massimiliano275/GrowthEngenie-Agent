# Pre-registrazione — Fase 2B: la strategia di produzione, 5 slot contro 10

| Campo | Valore |
| --- | --- |
| Data di registrazione | 2026-10-29 |
| Autore | Claude Code, su richiesta di Massimiliano |
| Oggetto | GrowthEngenie3ST come gira in produzione, con 5 slot (scelta dell'utente) e 10 slot (riferimento) |
| Codice di riferimento | repo del bot, commit `10ce75a` (29/10/2026): `core/sniper_engine.py`, `core/portfolio_5slot.py`, `core/asset_strategy.py`; `config.json` della VM: `"TIMEFRAME": "1d"` (verificato il 29/10) |
| Motore | Vibe-Trading 0.1.18, calibrato nella Fase 2A (scarto max 0,086 pp a regole uguali) |

## 1. Ipotesi

Misura descrittiva: quanto rende e quanto rischia la strategia di produzione, e che cosa cambia passando da 10 a 5 slot.
Non è un test di promozione: la scelta resta all'utente, sui numeri e sui controlli qui sotto.

## 2. Regole (traduzione fedele della produzione)

- **Universo**: i 64 perp Binance USD-M del registry (`_backpack_all_perps` filtrato da `_get_perp_symbols`), come nella run del 25/10. Simboli mancanti su Binance esclusi come in produzione.
- **Scan (selezione)**, a ogni chiusura 4H, da `scan_single_st_1h` e `rank_single_st_1h_candidates`:
  - ST(6, 2,0) di Wilder (`_supertrend`) sulle candele 4H chiuse; asset valido con almeno 120 barre 4H;
  - fresco = flip da ≤ 3 barre 4H (barra corrente inclusa), con conferma: ST(6, 2,0) sull'ultima candela **1D chiusa** concorde (servono ≥ 49 candele 1D chiuse);
  - punteggio = bucket (100 se ≤ 2 barre, altrimenti 50) + RS 1 barra vs BTC (×1,5, 0-15) + volume sopra la media delle 40 barre precedenti (0-10);
  - se restano slot vuoti: leader in trend (> 3 barre, 1D concorde, RS ≥ 1%, volume ≥ +25%).
- **Ingresso**: nella direzione del flip 4H, all'open della barra 4H successiva.
- **Uscita** (`asset_strategy.evaluate`, `live_exit=True`, TIMEFRAME 1d): ST(6, 2,0) **giornaliero sulla candela in formazione**; si esce quando la sua direzione è opposta alla posizione. Ricostruzione: a ogni chiusura 4H la candela del giorno parziale (open del giorno, max e min fin lì, close 4H corrente) e un passo della ricorsione di `_supertrend` dallo stato dell'ultimo giorno chiuso. Se il segnale non è disponibile (storia insufficiente) si tiene la posizione, come in produzione.
- **Ordine nella barra**: prima le uscite, poi il riempimento degli slot liberi. Un asset appena chiuso può essere riscelto nella stessa barra, come in produzione (nessuna guardia: la strategia viene rimossa alla chiusura).
- **Slot e dimensione**:
  - configurazione **5**: massimo 5 posizioni, 19% dell'equity ciascuna;
  - configurazione **10** (riferimento): massimo 10 posizioni, 9,5% ciascuna.
- Avvio con slot vuoti il 01/07/2024.

## 3. Dati e periodo

- Binance USD-M 4H con mark price e funding storico (lanciatore `run_backtest_listing_safe.py`: tolleranze solo sui bordi di quotazione e sul delisting, stampate).
- Dati dal 01/05/2024 (riscaldamento); valutazione dal 01/07/2024 al 30/09/2026, come la run del 25/10.
- Survivorship: l'universo è il registry di oggi. Limite dichiarato, non corretto qui.

## 4. Costi

- Commissione 0,05% per lato (Backpack Tier 1 taker, apertura e chiusura); slippage 0,05% per lato.
- Funding storico Binance (`funding_mode: data`, non strict).

## 5. Metriche

Per ciascuna configurazione: rendimento totale e annuo, drawdown massimo, Sharpe, numero di operazioni, operazioni vincenti, profit factor, esposizione media, commissioni pagate, funding netto; **rientri immediati** (stesso asset riaperto entro 1 barra dalla chiusura) come misura del ricambio.

## 6. Controlli obbligatori

1. **Fedeltà**: le feature dello scan contro le funzioni di produzione su timestamp casuali (come il 25/10: atteso 100%), e la direzione giornaliera in formazione contro `_supertrend` di produzione applicato a "giorni chiusi + candela parziale" (atteso 100%).
2. **Meccanica**: mai più di N posizioni, pesi solo ±19% o ±9,5%, somma ≤ 95%, commissioni 5 bp per fill.
3. **Limite dichiarato**: la produzione valuta l'uscita ogni minuto, il simulatore a ogni chiusura 4H. Il ricambio in produzione può essere più alto di quello misurato.

## 7. Cosa NON si farà

- Nessun altro numero di slot o peso oltre ai due registrati.
- Nessuna modifica dei parametri dopo i risultati.
- Nessuna modifica al bot di produzione in questa fase.
