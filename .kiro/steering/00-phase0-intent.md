# Phase 0: Intent Capture Protocol

Quando l'utente richiede nuova infrastruttura o modifiche architetturali:
1. NON invocare tool per creare file con estensione `.tf`.
2. Leggi il modello da `.kiro/templates/intent.template.md`.
3. Estrai le entità dal messaggio dell'utente e popola i campi corrispondenti.
4. Per i campi non specificati dall'utente:
   - Usa i valori di default più conservativi definiti nel template.
   - Non inventare chiavi o strutture fuori dallo schema.
5. Scrivi il risultato nel file `infra-intent.md` alla radice del workspace.
6. Mostra all'utente un riepilogo puntuale delle assunzioni fatte e chiedi conferma 
   esplicita prima di passare alla fase successiva.