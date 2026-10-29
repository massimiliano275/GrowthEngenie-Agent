# Fase 2A — riproduzione della baseline di ricerca (29/10/2026)

Comando (errata della pre-registrazione):

    python research/sweep_may_vs_fixed.py --wf_filters --wf_exits --tf 4h --asof 2026-10-01

Log completo: `riproduzione_baseline.log`.

## Dati: identici alla baseline congelata

`[diag] fingerprint BTC: n=9000 somma_cl=564666046.2 ultimo=2026-09-30 20:00:00`, uguale a `PROMPT_RIPRESA.md`.

## Risultati: diversi dalla baseline congelata

| Variante | `PROMPT_RIPRESA.md` (19/10) | Oggi (29/10) |
| --- | ---: | ---: |
| tier A, totale / annuo | 346,8% / 53,4% | 937,7% / 118,1% |
| equal A, totale / annuo | 75,7% / 17,5% | 195,5% / 43,5% |
| E4 tier, totale / annuo | 104,3% / 22,6% | 398,8% / 70,9% |
| fold | finestra dichiarata 2024-07-01 → 2026-09-30 | 6 fold di test, 2023-08 → 2026-08 (36 mesi) |

Lo script è entrato nella repo il 22/10 (commit `60d4e0d`) e non è più cambiato; nessuna copia della versione
del 19/10 è stata trovata sul PC né nell'archivio su D:. **La baseline del 19/10 non è riproducibile**;
il riferimento per la calibrazione è questa riproduzione.

Per fold (tier, variante A): 139,1% · 59,6% · 91,1% · −19,6% · 48,9% · 18,8%. Stop E1-E3b mai eseguiti (0).

Documentazione: il comando in `PROMPT_RIPRESA.md` (righe 83 e 96) non include `--wf_filters` e `--tf 4h`;
senza `--wf_filters` lo script esegue un altro esperimento senza avvisare.
