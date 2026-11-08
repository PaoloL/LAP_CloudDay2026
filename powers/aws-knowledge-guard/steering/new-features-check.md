# AWS: verifica di servizi e funzionalita' nuovi

Da usare quando scegli un servizio o una funzionalita' per una soluzione, quando l'utente chiede cosa c'e'
di nuovo, o quando la tua conoscenza di un servizio potrebbe essere superata.

## 1. Cerca gli annunci recenti
- `search_documentation` con topic `current_awareness` e una frase specifica
  (es. "ECS Fargate new features", "API Gateway HTTP API launch").
- Leggi con `read_documentation` gli annunci rilevanti e annota titolo, data e URL.
- Considera "nuovo" tutto cio' che non conoscevi o che e' stato pubblicato dopo il tuo cutoff: non scartarlo
  perche' non lo ricordi.

## 2. Confronta con la soluzione proposta
Per ogni servizio scelto chiediti, e verifica nella documentazione:
- esiste una funzionalita' recente che semplifica la soluzione o sostituisce un workaround che stavi per proporre?
- quello che stavi per usare e' stato deprecato, rinominato o messo in fine supporto?
- e' cambiato un limite o un default rilevante?

## 3. Verifica la disponibilita' nella regione
- `get_regional_availability` per il servizio, la funzionalita' o la risorsa CloudFormation nella regione del
  progetto (es. `eu-west-1`).
- Se non e' disponibile, proponi alternative (altra regione o altro servizio) e chiedi conferma all'utente.

## 4. Controlla che Terraform lo supporti
Una funzionalita' annunciata da AWS non e' detto che sia gia' nel provider `hashicorp/aws` della versione del
progetto. Se il power `terraform-knowledge-guard` e' attivo, verifica li' la risorsa o l'argomento; altrimenti
segnala il rischio all'utente.

## Cosa riportare
- Annunci e pagine consultati (titolo, data, URL).
- Novita' che cambiano la soluzione, e come.
- Esito della verifica regionale.
- Cosa non e' stato possibile verificare.
