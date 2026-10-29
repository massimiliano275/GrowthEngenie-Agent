# Pre-registrazione — <nome del test>

Copia questo file come `AAAA-MM-GG_<nome>.md` **prima** di eseguire qualsiasi test. Dopo aver visto i risultati non si modifica: un cambiamento è un nuovo file con una nuova data.

| Campo | Valore |
| --- | --- |
| Data di registrazione | AAAA-MM-GG |
| Autore | |
| Strategia o filtro | |
| Versione del codice | commit o tag git |

## 1. Ipotesi

Una frase verificabile: cosa ci si aspetta e perché.

## 2. Regole e parametri (congelati)

- Regole d'ingresso e d'uscita, senza ambiguità
- Timeframe ed esecuzione (es. apertura della barra successiva)
- Parametri con i loro valori esatti

## 3. Dati e periodo

- Fonte, strumenti, timeframe
- Periodo di sviluppo e periodo di test (mai usato prima)
- Trattamento di survivorship, dati mancanti, quotazioni e delisting

## 4. Costi

- Commissioni per lato, slippage, funding (fonte)

## 5. Metriche

- Metrica principale e metriche secondarie, con la formula

## 6. Criteri di successo e di fallimento

- Successo se: ...
- Fallimento se: ...
- Controlli obbligatori: look-ahead, ricorsione degli indicatori, robustezza dei parametri (mappa, non ottimizzazione), periodo mai usato

## 7. Cosa NON si farà

- Nessuna modifica ai parametri dopo i risultati
- Nessuna scelta di nuovi parametri dalla mappa di robustezza
