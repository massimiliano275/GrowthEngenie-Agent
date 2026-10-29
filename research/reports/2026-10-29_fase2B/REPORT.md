# Fase 2B — La strategia di produzione: 5 slot contro 10 (resoconto)

Data: 29/10/2026 · Modalità: validazione · Pre-registrazione: `research/preregistration/2026-10-29_fase2B_produzione_5_vs_10_slot.md`
Motore: Vibe-Trading 0.1.18 (calibrato in Fase 2A). Codice: `vibe_trading/runs/prod_5slot` e `prod_10slot`.

## Controlli pre-registrati

| Controllo | Esito |
| --- | --- |
| Fedeltà dello scan alla produzione | 100% su 2.103 confronti (25/10) |
| Fedeltà dell'uscita (ST 1D in formazione) | **100% su 2.560 confronti** contro `_supertrend` di produzione su giorni chiusi + candela parziale |
| Posizioni massime | 5 e 10, mai superate |
| Pesi | solo ±0,19 e ±0,095; somma massima 0,95 |
| Commissioni | 5,0 bp per fill in entrambe |

## Risultati (01/07/2024 → 30/09/2026, 1.000 $ iniziali)

| Metrica | 5 slot × 19% | 10 slot × 9,5% |
| --- | ---: | ---: |
| Capitale finale | 321,26 $ | 1.700,23 $ |
| Rendimento totale | −67,9% | +70,0% |
| Rendimento annuo | −39,6% | +26,6% |
| Drawdown massimo | −81,7% | −54,7% |
| Sharpe | −0,47 | 0,69 |
| Operazioni | 240 | 440 |
| Vincenti | 32,1% | 34,8% |
| Profit factor | 0,74 | 1,24 |
| Durata media | 102,6 giorni | 111,7 giorni |
| Posizioni medie aperte | 4,99 su 5 | 9,97 su 10 |
| Commissioni | 25,18 $ | 38,59 $ |
| Funding netto (ricostruito; positivo = pagato) | 35,65 $ | −29,97 $ (incassato) |
| Rientri immediati (stesso asset entro 1 barra) | 8 | 17 |
| Benchmark (paniere equipesato) | −17,0% | −17,0% |

## Da dove viene la differenza

- **Slot sempre pieni.** Con l'uscita sul ST giornaliero le posizioni durano in media 100-110 giorni e gli slot sono
  occupati il 99,8-99,7% del tempo: un flip nuovo entra solo quando un occupante esce.
- **Il risultato a 10 slot è fatto da due operazioni.** P&L totale +706 $; ZEC long +457 $ (un trade da +989% in
  98 giorni) e VVV +316 $. Le altre 438 operazioni insieme fanno −67 $.
- **A 5 slot ZEC e VVV non sono mai entrati**: gli slot erano occupati quando hanno girato. I primi ingressi sono
  gli stessi nei due casi (DOT, SOL, CRV, TIA, SUI…); poi le storie si separano.

Lettura (validazione): la differenza tra 5 e 10 slot misura soprattutto **se un movimento eccezionale trova uno slot
libero nel momento in cui parte**. Con una sola storia non si può dire se 5 slot sia peggio per struttura o per caso.

## Alternativa concreta: la ripetibilità della cattura

Test da pre-registrare: stessa strategia, stesse due configurazioni, **date di avvio diverse** (per esempio ogni
2 settimane da luglio 2024 a giugno 2025, a slot vuoti). Misura: distribuzione del rendimento e quota di partenze
in cui i movimenti eccezionali (ZEC, VVV e simili) vengono catturati. È la domanda giusta per un trend-following
che vive di pochi trade enormi: non "senza quei trade?", ma "quante volte li prende?".

## Limiti

- Universo di oggi (survivorship).
- Uscita valutata a ogni chiusura 4H; la produzione la valuta ogni minuto.
- Funding: Binance (8 ore e 4 ore), non Backpack (orario).
