# Phase 1b: Design Tokens via MCP

Il server MCP `platform-context-engine` è la fonte dei valori di ambiente.
Quando generi o modifichi file Terraform da 'infra-intent.md':

1. VALORI DI AMBIENTE: chiama il tool `read_design_tokens` con `environment` preso da 'infra-intent.md'
   e uno dei domini `network`, `security`, `compute`, `storage`, `governance`.
   - NON leggere 'platform/tokens/*.yaml' con tool di lettura file o con comandi di shell.
   - NON inventare né ricordare a memoria VPC, subnet, ARN KMS, TLS policy, dimensionamento, naming mask o tag.
   - Se il tool restituisce un campo `error`, FERMATI e riporta l'errore all'utente.
2. SCHEMA DEL PROVIDER: non è compito di questo server. Prima di scrivere o modificare una risorsa AWS,
   segui il power `terraform-knowledge-guard` (documentazione del Terraform Registry per la versione del
   provider del progetto, tool `search_providers` e `get_provider_details`).
3. TRACCIA: nel riepilogo finale elenca quali chiamate MCP hai fatto (tool, ambiente, dominio o tipo di risorsa).
   Se il server MCP non è disponibile, dillo all'utente e NON ripiegare sulla lettura diretta dei file.
4. Il nome dell'ambiente `prod` corrisponde al file di token `prd.yaml`: la mappatura è fatta dal server.
