# Requirements Document

## Introduction

Questa feature genera l'infrastruttura AWS del servizio `garage-management` per l'ambiente **dev**, partendo da `infra-intent.md`. I valori specifici dell'ambiente (rete, chiavi KMS, dimensionamento, naming, tag) non vengono scritti a mano: sono risolti dai Design Tokens aziendali tramite il server MCP `platform-context-engine`, a partire da `platform/tokens/dev.yaml`.

Il risultato è codice Terraform (provider AWS `~> 5.0`, solo risorse primitive) per un'API HTTP pubblica con endpoint per garage, auto e moto, un container Fargate piccolo, una tabella DynamoDB e un bucket S3 per le foto dei veicoli.

Lo stato attuale del workspace: `infra-intent.md` dichiara `environment: prod` e la cartella `terraform/` contiene valori di prod scritti direttamente nei file. Questa feature deve rendere la generazione ripetibile per `dev`.

## Glossary

- **Intent_File**: il file `infra-intent.md` alla radice del workspace, che descrive servizio, API, compute e storage.
- **Design_Tokens**: i valori aziendali per ambiente nei file `platform/tokens/{env}.yaml`.
- **Token_Resolver**: il tool MCP `read_design_tokens` del server `platform-context-engine`.
- **Schema_Inspector**: i tool `search_providers` e `get_provider_details` del power `terraform-knowledge-guard` (Terraform MCP server remoto di HashiCorp), letti alla versione del provider del progetto.
- **Generator**: l'agente Kiro che produce i file Terraform dall'Intent_File e dai Design_Tokens.
- **Terraform_Module_Dir**: la cartella `terraform/` che contiene i file `.tf` generati.
- **Naming_Mask**: la formula `acme-{environment}-{service_name}-{resource_suffix}`.
- **Photos_Bucket**: il bucket S3 che conserva le foto dei veicoli.
- **Primary_Table**: la tabella DynamoDB a tabella singola con chiavi `PK` e `SK`.
- **Api_Service**: il service ECS Fargate che esegue l'API.
- **Vpc_Link_Ingress**: l'insieme di HTTP API di API Gateway, VPC Link e ALB interno che espone l'Api_Service.

## Requirements

### Requirement 1: Intent per l'ambiente dev

**User Story:** Come platform engineer, voglio che l'Intent_File descriva l'ambiente dev, così che la generazione parta da una fonte unica e confermata.

#### Acceptance Criteria

1. WHEN l'utente richiede la generazione per l'ambiente dev, THE Generator SHALL aggiornare l'Intent_File con `environment: "dev"` e mostrare all'utente le assunzioni fatte.
2. THE Generator SHALL ottenere la conferma esplicita dell'utente sull'Intent_File prima di generare qualsiasi file `.tf`.
3. THE Intent_File SHALL rispettare lo schema di `.kiro/templates/intent.template.md` senza chiavi aggiuntive.
4. THE Intent_File SHALL dichiarare `service_name: "garage-management"`, `exposure: "public"`, `compute.size: "small"` e `compute.port: 8080`.
5. THE Intent_File SHALL elencare le route CRUD per `/garages`, `/cars` e `/motorcycles`, con parametri di path in snake_case.
6. THE Intent_File SHALL abilitare lo storage NoSQL con chiavi `PK` e `SK` e lo storage blob con scopo `vehicle-photos`.

### Requirement 2: Risoluzione dei Design Tokens

**User Story:** Come platform engineer, voglio che i valori di ambiente arrivino dai Design Tokens, così che il codice generato non contenga valori inventati.

#### Acceptance Criteria

1. WHEN l'Intent_File dichiara `environment: "dev"`, THE Generator SHALL invocare il Token_Resolver per i domini `network`, `security`, `compute`, `storage` e `governance` con `environment=dev`.
2. IF il Token_Resolver restituisce un errore, THEN THE Generator SHALL interrompere la generazione e riportare all'utente il messaggio di errore.
3. THE Generator SHALL ricavare dai Design_Tokens VPC, subnet, ARN delle chiavi KMS, TLS policy, profilo Fargate, `desired_count`, parametri S3 e DynamoDB, Naming_Mask e tag di default.
4. THE Generator SHALL NOT introdurre nel codice Terraform valori di ambiente che non compaiono nei Design_Tokens di dev.
5. THE Generator SHALL usare il profilo Fargate `small` di dev (256 CPU, 512 MB) e `desired_count` 1.

### Requirement 3: Validità dello schema del provider

**User Story:** Come platform engineer, voglio che gli attributi Terraform siano validi per la versione del provider installata, così che il codice non usi attributi inesistenti o deprecati.

#### Acceptance Criteria

1. WHEN il Generator definisce un tipo di risorsa AWS, THE Generator SHALL verificarne gli attributi con lo Schema_Inspector.
2. IF lo Schema_Inspector indica che un attributo o un blocco non esiste, THEN THE Generator SHALL correggere la risorsa prima di completare la generazione.
3. THE Terraform_Module_Dir SHALL usare il provider `hashicorp/aws` con vincolo di versione `~> 5.0`.
4. THE Generator SHALL NOT usare moduli Terraform preesistenti, ma solo risorse primitive del provider AWS.

### Requirement 4: Storage S3 per le foto

**User Story:** Come gestore di garage, voglio salvare le foto dei veicoli in modo privato e cifrato, così che non siano esposte pubblicamente.

#### Acceptance Criteria

1. THE Generator SHALL creare il Photos_Bucket con un `aws_s3_bucket` chiamato secondo la Naming_Mask con suffisso `photos`.
2. THE Generator SHALL creare un `aws_s3_bucket_public_access_block` con tutti e quattro i flag a `true`.
3. THE Generator SHALL creare un `aws_s3_bucket_server_side_encryption_configuration` che usa la chiave KMS di storage dei Design_Tokens di dev.
4. THE Photos_Bucket SHALL usare `force_destroy` e stato del versioning pari ai valori `storage.s3` di dev.
5. THE Photos_Bucket SHALL inviare i log di accesso al bucket indicato in `audit_log_target_bucket` di dev.

### Requirement 5: Storage DynamoDB

**User Story:** Come sviluppatore dell'API, voglio una tabella DynamoDB cifrata, così che garage, auto e moto siano salvati in modo persistente.

#### Acceptance Criteria

1. THE Generator SHALL creare la Primary_Table con `billing_mode = "PAY_PER_REQUEST"`, chiave di partizione `PK` e chiave di ordinamento `SK`, entrambe di tipo stringa.
2. THE Primary_Table SHALL avere `server_side_encryption` abilitata con la chiave KMS del database dei Design_Tokens di dev.
3. THE Primary_Table SHALL usare il valore `point_in_time_recovery` di dev e il valore `enable_deletion_protection` di dev come protezione dalla cancellazione.
4. THE Primary_Table SHALL chiamarsi secondo la Naming_Mask con suffisso `primary`.

### Requirement 6: Compute ECS Fargate

**User Story:** Come platform engineer, voglio un container Fargate piccolo e privato per l'API, così che il servizio non sia raggiungibile direttamente da Internet.

#### Acceptance Criteria

1. THE Generator SHALL creare un `aws_ecs_cluster`, un `aws_ecs_task_definition` Fargate e un `aws_ecs_service`.
2. THE Api_Service SHALL usare solo le subnet `private_app` di dev e `assign_public_ip = false`.
3. THE Api_Service SHALL esporre la porta 8080 e ricevere traffico solo dall'ALB interno.
4. THE task definition SHALL passare al container i nomi della Primary_Table e del Photos_Bucket come variabili d'ambiente.
5. THE Generator SHALL creare un ruolo del task con permessi limitati alla Primary_Table, al Photos_Bucket e alle chiavi KMS di dev, senza `Action: "*"` né `Resource: "*"`.
6. THE task definition SHALL inviare i log a un log group di CloudWatch.

### Requirement 7: API HTTP pubblica

**User Story:** Come client dell'API, voglio endpoint pubblici per garage, auto e moto, così che possa gestire i veicoli via HTTP.

#### Acceptance Criteria

1. THE Generator SHALL creare un `aws_apigatewayv2_api` di tipo HTTP.
2. THE Generator SHALL creare un `aws_apigatewayv2_vpc_link` verso le subnet `private_app` di dev.
3. THE Generator SHALL creare un ALB interno nelle subnet `private_app` di dev, con listener HTTPS che usa la TLS policy dei Design_Tokens di dev, davanti all'Api_Service.
4. THE Generator SHALL creare una `aws_apigatewayv2_route` per ogni route dichiarata nell'Intent_File.
5. WHEN una richiesta arriva su una route dichiarata, THE Vpc_Link_Ingress SHALL inoltrarla all'Api_Service tramite VPC Link.
6. THE Generator SHALL abilitare gli access log dello stage di API Gateway.

### Requirement 8: Naming e tag

**User Story:** Come responsabile dei costi e della governance, voglio nomi e tag coerenti, così che le risorse siano riconoscibili e attribuite al centro di costo corretto.

#### Acceptance Criteria

1. THE Generator SHALL nominare ogni risorsa che accetta un nome secondo la Naming_Mask, con `environment` pari a `dev`.
2. THE Generator SHALL applicare a tutte le risorse i tag di default di dev tramite `default_tags` del provider.
3. IF un nome risultante supera il limite di lunghezza del servizio AWS, THEN THE Generator SHALL accorciare il suffisso mantenendo prefisso e ambiente.

### Requirement 9: Parametrizzazione per ambiente

**User Story:** Come platform engineer, voglio che lo stesso codice Terraform serva più ambienti, così che dev e prod non divergano.

#### Acceptance Criteria

1. THE Terraform_Module_Dir SHALL ricevere i valori specifici di ambiente da variabili o da un file di valori per ambiente, non da costanti scritte nei file `.tf`.
2. WHEN il Generator viene eseguito per dev, THE Generator SHALL produrre valori coerenti con `platform/tokens/dev.yaml` senza modificare il comportamento della configurazione prod.
3. THE Terraform_Module_Dir SHALL richiedere come variabili l'immagine del container, l'ARN del certificato ACM e il nome DNS dell'ALB, senza valori di default.

### Requirement 10: Verifica del risultato

**User Story:** Come platform engineer, voglio sapere che il codice generato è valido prima di una qualsiasi applicazione, così che non arrivino errori in fase di deploy.

#### Acceptance Criteria

1. WHEN la generazione è completata, THE Generator SHALL eseguire `terraform fmt` e `terraform validate` e riportare l'esito.
2. IF `terraform validate` fallisce, THEN THE Generator SHALL correggere gli errori e rieseguire la validazione.
3. THE Generator SHALL NOT eseguire `terraform apply` senza una richiesta esplicita dell'utente.
4. THE Generator SHALL elencare all'utente i valori dei Design_Tokens che sembrano segnaposto, come ID di VPC e subnet o ARN di chiavi KMS non reali.
