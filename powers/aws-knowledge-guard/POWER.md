---
name: "aws-knowledge-guard"
displayName: "AWS Knowledge Guard"
description: "Supera il knowledge cutoff dell'LLM su AWS: nuovi servizi e funzionalita', annunci What's New, documentazione aggiornata e disponibilita' per regione, letti a runtime dall'AWS Knowledge MCP server remoto."
keywords: ["aws", "amazon", "servizio", "service", "nuovo", "new feature", "funzionalita'", "what's new", "annuncio", "launch", "documentazione", "docs", "regione", "region", "disponibilita'", "availability", "best practice", "well-architected", "quota", "limite", "arn", "knowledge cutoff"]
author: "maverick"
---

# AWS Knowledge Guard

Il tuo training ha un cutoff: AWS annuncia nuovi servizi e funzionalita' ogni giorno, li estende a nuove
regioni e aggiorna limiti e best practice. Questo power ti collega all'**AWS Knowledge MCP server**
(`https://knowledge-mcp.global.api.aws`), il server remoto ufficiale di AWS con documentazione, annunci
What's New, blog, Well-Architected e disponibilita' regionale di servizi, API e risorse CloudFormation.

**Regola d'oro: prima di proporre un servizio, una funzionalita', una regione o un limite "a memoria",
verificalo con la documentazione o con gli annunci recenti.**

# Onboarding

Nessuna installazione e nessun account AWS: il server e' pubblico e gratuito, con limiti di frequenza.
In Kiro CLI esegui `/mcp` (o `/tools`): il server `aws-knowledge` deve risultare connesso.

Non configurare insieme anche l'AWS MCP Server o l'AWS API MCP server: AWS sconsiglia di usarli in parallelo
con questo, perche' tool duplicati confondono l'agente.

# Tool del server (`aws-knowledge`)

| Tool | Quando usarlo |
| :--- | :--- |
| `search_documentation` | Cercare documentazione, annunci e guide. Usa il topic `current_awareness` per novita' e annunci What's New, `reference_documentation` per API e configurazione, `troubleshooting` per errori. |
| `read_documentation` | Leggere per intero una pagina trovata (docs.aws.amazon.com, aws.amazon.com/about-aws/whats-new, blog). |
| `recommend` | Trovare pagine collegate, incluse quelle aggiunte di recente, a partire da una pagina gia' letta. |
| `list_regions` | Elenco aggiornato delle regioni AWS con identificativi e nomi. |
| `get_regional_availability` | Verificare se un servizio, una funzionalita', un'API o una risorsa CloudFormation e' disponibile in una regione. |

In Kiro i nomi possono comparire con un prefisso (es. `aws___search_documentation`).

# Workflow steering (carica solo quello che serve)
- Scegliere un servizio o una funzionalita', o rispondere a "cosa c'e' di nuovo" -> `new-features-check.md`
- Regioni, limiti, ARN, best practice durante la progettazione -> `aws-workflow.md`

# Regole di comportamento
1. Mai affidarsi alla memoria per l'esistenza di servizi e funzionalita', la disponibilita' regionale, i limiti
   o i formati ARN: verifica con i tool.
2. Cita sempre la fonte: URL della pagina e, per gli annunci, la data di pubblicazione.
3. Se il server non e' raggiungibile, non trova nulla o supera i limiti di frequenza, **fermati e riportalo**;
   non ripiegare su valori ricordati e non presentarli come verificati.
4. Il server non vede il tuo account AWS: le quote che trovi sono i valori **predefiniti** documentati, non
   quelli applicati all'account. Dillo quando li usi.
