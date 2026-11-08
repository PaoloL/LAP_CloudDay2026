# Implementation Plan: garage-app

## Overview

Il piano rende parametrico il codice Terraform in `terraform/`, genera i valori dell'ambiente dev dai Design Tokens e verifica il risultato. Ogni passo modifica solo ciò che serve per dev e lascia invariato il comportamento di prod.

## Tasks

- [ ] 1. Aggiornare e confermare l'intent per dev
  - [ ] 1.1 Impostare `environment: "dev"` in `infra-intent.md`
    - Mantenere lo schema di `.kiro/templates/intent.template.md` senza chiavi aggiuntive
    - Mantenere servizio, route CRUD, compute `small` sulla porta 8080, tabella `PK`/`SK` e bucket `vehicle-photos`
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6_
  - [ ] 1.2 Mostrare le assunzioni all'utente e ottenere la conferma esplicita
    - Non generare file `.tf` finché la conferma non arriva
    - _Requirements: 1.1, 1.2_

- [ ] 2. Risolvere i Design Tokens di dev
  - [ ] 2.1 Leggere i token con `read_design_tokens` per `network`, `security`, `compute`, `storage` e `governance` con `environment=dev`
    - Fermarsi e riportare l'errore se un dominio restituisce `error`
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ] 2.2 Creare `terraform/environments/dev.tfvars` con la mappa token → variabile del design
    - Usare il profilo `small` (256 CPU, 512 MB) e `desired_count` 1
    - Non aggiungere valori che non sono nei token di dev
    - _Requirements: 2.3, 2.4, 2.5, 9.1_
  - [ ] 2.3 Creare `terraform/environments/prod.tfvars` con i valori oggi presenti in `locals.tf`
    - Ricavarli dai token di `prd.yaml` con `environment=prod`
    - _Requirements: 9.2_

- [ ] 3. Rendere parametrica la base di Terraform
  - [ ] 3.1 Aggiungere in `variables.tf` le variabili di ambiente con le `validation` del design
    - Variabili: `environment`, `aws_region`, `vpc_id`, `private_subnet_ids`, `storage_kms_key_arn`, `database_kms_key_arn`, `tls_policy`, `enable_deletion_protection`, `fargate_cpu`, `fargate_memory`, `desired_count`, `s3_force_destroy`, `s3_versioning_status`, `audit_log_bucket`, `dynamodb_pitr_enabled`, `naming_mask`, `default_tags`
    - Lasciare senza default `container_image`, `acm_certificate_arn` e `alb_internal_domain_name`
    - _Requirements: 9.1, 9.3_
  - [ ] 3.2 Ridurre `locals.tf` a `service_name`, `name_prefix` ricavato dalla `naming_mask`, `container_port` e `api_routes`
    - Rimuovere VPC, subnet, ARN KMS, dimensionamento e tag
    - _Requirements: 8.1, 9.1_
  - [ ] 3.3 Aggiornare `versions.tf` per usare `var.aws_region` e `var.default_tags`
    - Mantenere il vincolo `hashicorp/aws ~> 5.0`
    - _Requirements: 3.3, 8.2_

- [ ] 4. Verificare lo schema del provider
  - [ ] 4.1 Per ogni tipo di risorsa usato, leggere la documentazione con `search_providers` e `get_provider_details` (power `terraform-knowledge-guard`) alla versione del provider in `.terraform.lock.hcl`
    - Tipi: `aws_s3_bucket`, `aws_s3_bucket_public_access_block`, `aws_s3_bucket_server_side_encryption_configuration`, `aws_s3_bucket_versioning`, `aws_s3_bucket_logging`, `aws_dynamodb_table`, `aws_ecs_cluster`, `aws_ecs_task_definition`, `aws_ecs_service`, `aws_lb`, `aws_lb_target_group`, `aws_lb_listener`, `aws_apigatewayv2_api`, `aws_apigatewayv2_vpc_link`, `aws_apigatewayv2_integration`, `aws_apigatewayv2_route`, `aws_apigatewayv2_stage`
    - Correggere ogni attributo o blocco che non esiste
    - _Requirements: 3.1, 3.2, 3.4_

- [ ] 5. Parametrizzare le risorse
  - [ ] 5.1 Aggiornare `s3.tf`
    - Usare `var.s3_force_destroy`, `var.s3_versioning_status`, `var.audit_log_bucket` e `var.storage_kms_key_arn`
    - Mantenere il public access block con tutti i flag a `true`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ] 5.2 Aggiornare `dynamodb.tf`
    - Usare `var.dynamodb_pitr_enabled`, `var.enable_deletion_protection` e `var.database_kms_key_arn`
    - Mantenere `PAY_PER_REQUEST` e la cifratura abilitata
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [ ] 5.3 Aggiornare `ecs.tf` e `iam.tf`
    - Usare `var.fargate_cpu`, `var.fargate_memory`, `var.desired_count`, `var.private_subnet_ids` e `var.aws_region`
    - Mantenere `assign_public_ip = false` e i permessi minimi, senza `Action: "*"` né `Resource: "*"`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  - [ ] 5.4 Aggiornare `network.tf` e `apigw.tf`
    - Usare `var.vpc_id`, `var.private_subnet_ids`, `var.tls_policy` e `var.enable_deletion_protection`
    - Mantenere una route per ogni voce di `api_routes`, il VPC Link e gli access log dello stage
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 6. Gestire i limiti di lunghezza dei nomi
  - [ ] 6.1 Ricavare i nomi di ALB e target group con `substr(..., 0, 32)`
    - Aggiungere una `precondition` che fallisce se il prefisso lascia meno di 3 caratteri per il suffisso
    - _Requirements: 8.1, 8.3_

- [ ] 7. Checkpoint: formattazione e validazione
  - Eseguire `terraform fmt -recursive` e `terraform validate`, e controllare che il piano non usi attributi inesistenti
  - Correggere gli errori e rieseguire finché la validazione passa
  - Chiedere all'utente se ci sono dubbi prima di proseguire
  - _Requirements: 10.1, 10.2_

- [ ] 8. Verifiche aggiuntive
  - [ ]* 8.1 Scrivere in `tests/unit/` un test di coerenza tra `dev.yaml` e `dev.tfvars`
    - **Property 1: Fedeltà ai token**
    - **Validates: Requirements 2.3, 2.4, 2.5, 9.2**
  - [ ]* 8.2 Scrivere un test che cerca costanti di ambiente nei file `.tf`
    - Cercare `vpc-`, `subnet-`, `arn:aws:kms` e i letterali `dev` e `prod`
    - **Property 2: Nessuna costante di ambiente nei `.tf`**
    - **Validates: Requirements 9.1**
  - [ ]* 8.3 Scrivere un test sul prefisso dei nomi e sui limiti di lunghezza
    - **Property 3: Naming coerente**
    - **Validates: Requirements 8.1, 8.3**
  - [ ]* 8.4 Verificare con `validate` che `dev.tfvars` e `prod.tfvars` producano la stessa forma
    - **Property 4: Stessa forma, valori diversi**
    - **Validates: Requirements 9.2**
  - [ ]* 8.5 Verificare isolamento e cifratura in entrambi gli ambienti
    - **Property 5: Isolamento e cifratura sempre attivi**
    - **Validates: Requirements 4.2, 4.3, 5.2, 6.2**

- [ ] 9. Verifica finale e report
  - [ ] 9.1 Eseguire `terraform fmt -check` e `terraform validate` con `-var-file=environments/dev.tfvars` e con `prod.tfvars`
    - Non eseguire `terraform apply`
    - _Requirements: 10.1, 10.3_
  - [ ] 9.2 Elencare all'utente i valori dei token che sembrano segnaposto
    - Controllare ID di VPC e subnet, ARN KMS e account AWS in `dev.yaml` e `prd.yaml`
    - _Requirements: 10.4_

## Notes

- Le attività con `*` sono facoltative: le regole del workspace richiedono i test solo su richiesta.
- Prima di un `plan` servono `container_image`, `acm_certificate_arn` e `alb_internal_domain_name`, e le credenziali AWS.
- Il confronto di `terraform plan` su prod resta manuale.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["2.1", "3.1"] },
    { "id": 3, "tasks": ["2.2", "2.3", "3.2", "3.3"] },
    { "id": 4, "tasks": ["4.1"] },
    { "id": 5, "tasks": ["5.1", "5.2", "5.3", "5.4"] },
    { "id": 6, "tasks": ["6.1"] },
    { "id": 7, "tasks": ["7"] },
    { "id": 8, "tasks": ["8.1", "8.2", "8.3", "8.4", "8.5"] },
    { "id": 9, "tasks": ["9.1", "9.2"] }
  ]
}
```
