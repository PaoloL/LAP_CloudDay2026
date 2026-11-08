# AWS: workflow anti-knowledge-cutoff in progettazione

## Regioni
- Usa `list_regions` per gli identificativi corretti, non la memoria.
- Prima di usare un servizio, una funzionalita' o una risorsa CloudFormation in una regione:
  `get_regional_availability`.
- Se non e' disponibile, proponi alternative e chiedi conferma.

## Limiti e quote
- Cerca i limiti con `search_documentation` (es. "Fargate service quotas", "API Gateway HTTP API quotas")
  e leggi la pagina "Quotas" o "Limits" del servizio con `read_documentation`.
- Questi sono i valori **predefiniti**: il valore applicato all'account puo' essere diverso. Dillo all'utente e,
  se il limite e' critico, suggerisci di controllarlo in Service Quotas.

## ARN e policy IAM
- Per il formato degli ARN cerca la pagina "Actions, resources, and condition keys" del servizio
  (`search_documentation` + `read_documentation`) e usa i formati riportati li'.
- In Terraform preferisci i riferimenti (`aws_x.y.arn`) a stringhe costruite a mano.
- Nelle policy IAM non usare `Resource: "*"` se il formato ARN consente di restringere.

## Best practice
- Per scelte di architettura (sicurezza, affidabilita', costi) cerca la guida Well-Architected o la
  documentazione del servizio e cita la pagina usata.

## Cosa riportare
- Pagine consultate (URL) per ogni decisione.
- Cosa e' un valore predefinito documentato e non un dato verificato sull'account.
