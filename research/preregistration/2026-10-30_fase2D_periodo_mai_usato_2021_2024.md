# Pre-registrazione — Fase 2D: periodo mai usato (gennaio 2021 → giugno 2024)

| Campo | Valore |
| --- | --- |
| Data di registrazione | 2026-10-30 |
| Autore | Claude Code, su richiesta di Massimiliano (ultima prova teorica prima di tornare allo sviluppo; il live resta manuale) |
| Motore | Vibe-Trading 0.1.18, calibrato in Fase 2A |
| Codice | identico alla Fase 2C (uscita sul flip ST 4H a candela chiusa, conferma 1D sugli ingressi), cambiano solo le date |

## 1. Ipotesi

Il confronto della Fase 2C (10 slot × 9,5% meglio di 5 slot × 19%) si ripete su un periodo che nessuna fase ha usato.

## 2. Regole

Identiche alla Fase 2C: scan su flip ST(6, 2,0) 4H fresco con conferma ST 1D, punteggio bucket + RS + volume, leader in
trend; uscita sul flip ST 4H a candela chiusa; esecuzione all'open 4H successivo. Configurazioni 5 × 19% e 10 × 9,5%.

## 3. Dati e periodo

- 64 perp Binance USD-M del registry di oggi; dati 4H dal 01/11/2020 (riscaldamento), valutazione dal 01/01/2021 al 30/06/2024.
- Una sola partenza (01/01/2021): la Fase 2C ha mostrato che partenze diverse convergono in pochi giorni.
- **Limite dichiarato, non correggibile qui**: universo scelto con il registry del 2026. Mancano i perp poi delistati
  (survivorship forte) e molti asset entrano nell'universo solo dalla loro quotazione.

## 4. Costi

Commissione 0,05% per lato, slippage 0,05% per lato, funding storico Binance (non strict).

## 5. Metriche

Rendimento totale e annuo, drawdown massimo, Sharpe, operazioni, durata media, catture ≥ +100%, numero di asset
attivi nel tempo; confronto 5 contro 10.

## 6. Criteri

- "Il confronto si ripete" se 10 slot ha rendimento annuo più alto **e** drawdown non peggiore di 5 slot, come in Fase 2C.
- Misura descrittiva: nessuna modifica alla produzione.

## 7. Cosa NON si farà

Nessun cambio di parametri, date o universo dopo i risultati.
