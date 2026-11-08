---
name: "terraform-knowledge-guard"
displayName: "Terraform Knowledge Guard"
description: "Supera il knowledge cutoff dell'LLM su Terraform: sintassi reale e attributi deprecati del provider hashicorp/aws, letti a runtime dal Terraform Registry tramite il Terraform MCP server remoto di HashiCorp."
keywords: ["terraform", "tf", "hcl", "provider", "hashicorp/aws", "aws_", "resource", "data source", "deprecated", "deprecato", "deprecation", "schema", "argomenti", "upgrade", "versione provider", "registry", "modulo", "iac", "knowledge cutoff"]
author: "maverick"
---

# Terraform Knowledge Guard

Il tuo training ha un cutoff: il provider `hashicorp/aws` rilascia nuove versioni ogni settimana, aggiunge
risorse, depreca e rimuove argomenti. Questo power ti collega al **Terraform MCP server remoto di HashiCorp**
(`https://mcp.terraform.io/mcp`), che legge la documentazione ufficiale del Terraform Registry per la versione
del provider che indichi.

**Regola d'oro: prima di scrivere il nome di una risorsa, di un argomento o di un blocco "a memoria",
verificalo nella documentazione del Registry per la versione del provider usata dal progetto.**

# Onboarding

## Step 1: Token HCP Terraform
Il server remoto richiede un account HCP Terraform (va bene il piano Free) e un API token (utente o team).
1. Crea il token: HCP Terraform -> User settings -> Tokens.
2. Aggiungi questa riga a `~/.kiro/.env` (il valore include la parola `Bearer` e uno spazio):
   ```
   HCP_TERRAFORM_AUTH_HEADER=Bearer <token>
   ```
3. `mcp.json` avvia `mcp-remote` tramite `dotenv`, che legge `~/.kiro/.env` e inoltra le richieste a
   `https://mcp.terraform.io/mcp` con l'header `Authorization`. Il token non va mai scritto in `mcp.json`.

Prerequisiti: `dotenv` (`brew install dotenv` o equivalente in `/opt/homebrew/bin`) e Node.js (`npx`).
Se il server risponde `Authorization bearer token is required`, la riga in `~/.kiro/.env` manca o e' scritta male.

## Step 2: Verifica
In Kiro CLI esegui `/mcp` (o `/tools`): il server `terraform-registry` deve risultare connesso e mostrare
tool come `search_providers` e `get_provider_details`.

# Tool del server (`terraform-registry`)

| Tool | Quando usarlo |
| :--- | :--- |
| `get_latest_provider_version` | All'inizio di ogni lavoro IaC: confronta l'ultima versione di `hashicorp/aws` con quella del progetto. |
| `search_providers` | Per trovare il documento di una risorsa, data source o guida (es. upgrade guide) e ottenere il suo ID, per una versione precisa del provider. |
| `get_provider_details` | Per leggere la documentazione completa di quella risorsa: argomenti, blocchi, attributi esportati, note di deprecazione. |
| `get_provider_capabilities` | Per una panoramica di cosa offre il provider (risorse, data source, funzioni). |
| `search_modules` / `get_module_details` | Solo se l'utente chiede un modulo: le regole del workspace possono vietarli. |

Il server remoto espone anche tool per workspace, run, team, variabili e registry privato di HCP Terraform.
Sono disattivati in `mcp.json` (`disabledTools`): questo power serve solo a leggere la documentazione pubblica
del Registry. Restano attivi i 9 tool del Registry pubblico, compresi `search_policies` e `get_policy_details`.

# Workflow steering
- Scrivere, rivedere o aggiornare file `.tf` -> `terraform-workflow.md`

# Regole di comportamento
1. Mai affidarsi alla memoria per nomi di risorse, argomenti, blocchi o valori ammessi: leggi la documentazione.
2. Leggi sempre la documentazione della **versione del provider usata dal progetto** (da `.terraform.lock.hcl`
   o dal vincolo in `versions.tf`), non dell'ultima: gli argomenti cambiano tra major version.
3. Se il server non e' raggiungibile o non trova il documento, **fermati e riportalo**; non ripiegare su
   valori ricordati e non presentarli come verificati.
4. Nel riepilogo finale elenca i documenti consultati (risorsa + versione) e cosa NON hai potuto verificare.
