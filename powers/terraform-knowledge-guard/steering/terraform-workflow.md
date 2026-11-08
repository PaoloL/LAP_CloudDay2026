# Terraform: workflow anti-knowledge-cutoff

Sequenza obbligatoria quando crei, modifichi o rivedi file `.tf` con risorse `aws_*`.

## 1. Versione del provider
- Leggi la versione installata da `.terraform.lock.hcl` (blocco `provider "registry.terraform.io/hashicorp/aws"`,
  campo `version`) e il vincolo dichiarato in `versions.tf`.
- Chiama `get_latest_provider_version` per `hashicorp/aws`.
- Se la major installata e' inferiore all'ultima, dillo all'utente. Non cambiare il vincolo senza il suo
  consenso: puo' cambiare il comportamento di risorse esistenti.

## 2. Documentazione di ogni risorsa che scrivi
Per ogni tipo di risorsa o data source:
1. `search_providers` con `provider_namespace = "hashicorp"`, `provider_name = "aws"`, il servizio
   (es. `s3_bucket_versioning`) e **la versione del progetto**.
2. `get_provider_details` con l'ID restituito.
3. Usa SOLO gli argomenti e i blocchi documentati. Rispetta quelli `Required`. Non assegnare gli attributi
   che compaiono solo in "Attribute Reference" (sono calcolati).
4. Evita tutto cio' che la documentazione marca come **Deprecated**, e usa l'alternativa che indica.

Se un argomento che ti aspettavi non c'e', cerca una risorsa dedicata: spesso una configurazione e' stata
estratta in `aws_<servizio>_<risorsa>_<funzione>` (es. versioning, cifratura e public access di S3 vivono in
risorse `aws_s3_bucket_*`).

## 3. Revisione di codice esistente (deprecazioni)
Per ogni risorsa gia' presente nei `.tf`:
- leggi la sua documentazione alla versione del progetto e confronta gli argomenti usati;
- elenca quelli marcati Deprecated, con file, risorsa e alternativa indicata.

## 4. Aggiornamento di major version (es. 5.x -> 6.x)
- `search_providers` cercando le guide (`guides`) del provider, in particolare la upgrade guide della nuova
  major (es. `version-6-upgrade`).
- `get_provider_details` sulla guida e confronta i cambiamenti con le risorse usate nel progetto.
- Riporta all'utente cosa si rompe e cosa va modificato **prima** di toccare il vincolo di versione.

## 5. Validazione
Il server legge solo la documentazione, non il tuo codice. Dopo ogni modifica, se puoi eseguire comandi,
lancia nella cartella Terraform:
```bash
terraform fmt -check && terraform validate
```
Tratta ogni warning di deprecazione come da correggere o da segnalare.

## Cosa riportare nel riepilogo
- Versione del provider del progetto vs ultima.
- Documenti consultati (risorsa + versione).
- Argomenti deprecati trovati e alternativa proposta.
- Esito di `terraform validate`, o il fatto che non e' stato eseguito.

## Limiti noti (non nasconderli)
- La documentazione non esprime tutti i vincoli semantici (combinazioni non ammesse, dipendenze tra risorse):
  emergono con `terraform plan`.
- Il server remoto e' in beta e ha bisogno del token HCP Terraform: se non risponde, dillo.
