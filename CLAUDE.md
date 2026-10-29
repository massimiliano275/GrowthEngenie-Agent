# GrowthEngenie — regole per ogni sessione

Fondo personale di trading multi-strategia, **solo con il capitale di Massimiliano**. Questo file vale in ogni sessione di Claude Code aperta in questa repo.

## Regole di lavoro

1. **Rispondere in italiano.**
2. **Implementazione e validazione separate.** Implementando non si giudicano i risultati; validando non si modifica il codice. Dichiarare sempre la modalità. La validazione di una strategia o di un componente si fa in una sessione separata, che non ha visto come è stato costruito.
3. **Ogni bug segnalato ha una prova:** file, riga esatta e input che lo fa fallire. Senza prova è un "sospetto" e si chiama così.
4. **Un risultato negativo si chiude con un'alternativa** concreta e praticabile.
5. **Pre-registrazione obbligatoria.** Prima di qualsiasi test su strategia o filtro: ipotesi, parametri, periodo, metriche, criteri di successo e fallimento in un file datato in `research/preregistration/` (modello: `TEMPLATE.md`). Nessun test senza quel file; nessuna modifica ai parametri dopo aver visto i risultati.
6. **Nessun ordine reale senza ok esplicito.** Niente chiavi API con permesso di trading finché non lo dice l'utente. Le chiavi stanno solo in `.env` (escluso da git), mai nel codice, nei log o nei messaggi.
7. **Operazioni irreversibili** (cancellare dati, sovrascrivere storici, toccare i bot in produzione, migrazioni distruttive): proporre, spiegare, aspettare conferma.
8. **Le informazioni sugli strumenti** vanno verificate sulle versioni installate prima di usarle.
9. **Il capitale è solo dell'utente.** Il sistema non prevede mai la gestione di denaro di terzi.

## Architettura (due piani che non si mescolano)

- **Ricerca** (locale, con l'utente, usa l'AI): produce pacchetti di strategia validati in `strategies/`.
- **Esecuzione** (VM GCP, 24/7, deterministica): fa girare solo strategie promosse. Nessun LLM generativo nel ciclo di trading; Jev ammesso solo come veto riduttivo, dopo la modalità ombra.
- **Promozione:** paper → live ridotto → live pieno, ogni passaggio con criteri oggettivi e ok dell'utente.
- **Il risk manager sta sopra a tutto:** contesto, Jev e allocatore possono solo ridurre l'esposizione.

## Struttura

| Cartella | Contenuto |
| --- | --- |
| `research/preregistration/` | file di pre-registrazione datati, `AAAA-MM-GG_nome.md` |
| `research/reports/` | resoconti di validazione |
| `research/notebooks/` | esplorazioni |
| `strategies/` | pacchetti validati: codice, parametri congelati, pre-registrazione, report, limiti di rischio |
| `services/` | collector, context, strategies, allocator, risk, executor, ledger, notifier |
| `db/` | schema e migrazioni |
| `infra/` | docker-compose, configurazioni della VM |
| `tests/` | test automatici |
| `tools/` | script di supporto (es. controllo segreti) |

## Da sapere

- Il bot in produzione GrowthEngenie3ST vive in un'altra repo (`growthengenie3st_backpack`) e **non si tocca** da qui: il nuovo sistema lo legge in sola lettura.
- La VM installa solo versioni con tag git.
- Hardware locale: i9, 32 GB di RAM, una sola GPU Radeon RX 550 da 4 GB (niente LLM locali su GPU).
