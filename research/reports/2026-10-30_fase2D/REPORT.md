# Fase 2D — Periodo mai usato (gennaio 2021 → giugno 2024): resoconto

Data: 30/10/2026 · Modalità: validazione · Pre-registrazione: `research/preregistration/2026-10-30_fase2D_periodo_mai_usato_2021_2024.md`
Teorico: il live è in modalità manuale.

## Esito

**Il confronto si ripete**: 10 slot × 9,5% ha rendimento annuo più alto (+29,7% contro −3,2%) e drawdown meno profondo
(−50,0% contro −74,1%) di 5 slot × 19%, come in Fase 2C. Lettura pre-registrata: **vera**.

## Risultati (1.000 $ iniziali, 01/01/2021 → 30/06/2024)

| Metrica | 5 slot × 19% | 10 slot × 9,5% |
| --- | ---: | ---: |
| Capitale finale | 892 $ | 2.484 $ |
| Rendimento totale / annuo | −10,8% / −3,2% | +148,4% / +29,7% |
| Drawdown massimo | −74,1% | −50,0% |
| Sharpe | 0,34 | 0,72 |
| Operazioni / vincenti | 1.355 / 35,2% | 2.372 / 36,8% |
| Profit factor | 1,05 | 1,15 |
| Durata media | 25,1 giorni | 25,8 giorni |
| Catture ≥ +100% | 5 | 13 |
| Commissioni | 465 $ | 506 $ |
| 2021 / 2022 / 2023 / 2024 (6 mesi) | +130,3% / −8,3% / −14,6% / −50,6% | +108,2% / +15,2% / +13,2% / −8,5% |
| Paniere equipesato dei 37 asset | +310,7% | +310,7% |

Controlli: posizioni massime 5 e 10; commissioni 5,0 bp per fill; occupazione media 4,45 su 5 e 8,00 su 10
(universo più piccolo e asset che entrano nel tempo).

## Limiti

- **Survivorship forte**: universo scelto dal registry del 2026. Nel periodo avevano dati 37 asset su 64; i 27 nati dopo
  (HYPE, PENGU, TRUMP, VVV…) esclusi perché inesistenti; i perp poi delistati (es. LUNA, FTT) mancano del tutto.
  Il paniere di confronto (+310,7%) è gonfiato dallo stesso bias.
- Una sola storia di mercato per periodo; 2021 è stato un anno di forte rialzo.
- Funding Binance, non Backpack.

## Sintesi delle Fasi 2B-2D (per la chat dedicata alla strategia)

| Fase | Uscita | Periodo | 5 slot | 10 slot |
| --- | --- | --- | ---: | ---: |
| 2B | ST 1D in formazione | 07/2024 → 09/2026 | −67,9% | +70,0% |
| 2C | flip ST 4H (26 partenze, una storia) | 07/2024 → 09/2026 | annuo mediano −8,0% | annuo mediano +27,8% |
| 2D | flip ST 4H | 01/2021 → 06/2024 | annuo −3,2% | annuo +29,7% |

In tutte e tre 10 slot fa meglio di 5, con drawdown minore. Con 5 slot la strategia perde occasioni (meno catture oltre
+100%) e concentra il rischio.

## Correzioni al lanciatore in questa fase

`run_backtest_listing_safe.py`: un perp senza alcuna candela nel periodo (non ancora quotato) ora restituisce un frame
vuoto ed è escluso dall'universo, come in produzione; elencati in `[non quotati nel periodo]`.
