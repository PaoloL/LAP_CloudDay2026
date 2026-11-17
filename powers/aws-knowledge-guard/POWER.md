---
name: "aws-knowledge-guard"
displayName: "AWS Knowledge Guard"
description: "Overcomes the LLM knowledge cutoff on AWS: new services and features, What's New announcements, up-to-date documentation and regional availability, read at runtime from the remote AWS Knowledge MCP server."
keywords: ["aws", "amazon", "service", "new feature", "feature", "what's new", "announcement", "launch", "documentation", "docs", "region", "availability", "best practice", "well-architected", "quota", "limit", "arn", "knowledge cutoff"]
author: "maverick"
---

# AWS Knowledge Guard

Your training has a cutoff: AWS announces new services and features every day, extends them to new Regions and
updates limits and best practices. This power connects you to the **AWS Knowledge MCP server**
(`https://knowledge-mcp.global.api.aws`), AWS's official remote server with documentation, What's New
announcements, blogs, Well-Architected guidance and regional availability of services, APIs and CloudFormation
resources.

**Golden rule: before proposing a service, a feature, a Region or a limit "from memory", check it against the
documentation or recent announcements.**

# Onboarding

No installation and no AWS account: the server is public and free, with rate limits.
In Kiro CLI run `/mcp` (or `/tools`): the `aws-knowledge` server must be connected.

Do not also configure the AWS MCP Server or the AWS API MCP server: AWS advises against using them alongside
this one, because duplicate tools confuse the agent.

# Server tools (`aws-knowledge`)

| Tool | When to use it |
| :--- | :--- |
| `search_documentation` | Search documentation, announcements and guides. Use the `current_awareness` topic for news and What's New announcements, `reference_documentation` for APIs and configuration, `troubleshooting` for errors. |
| `read_documentation` | Read a page you found in full (docs.aws.amazon.com, aws.amazon.com/about-aws/whats-new, blogs). |
| `recommend` | Find related pages, including recently added ones, starting from a page you already read. |
| `list_regions` | Up-to-date list of AWS Regions with identifiers and names. |
| `get_regional_availability` | Check whether a service, feature, API or CloudFormation resource is available in a Region. |

In Kiro the names may appear with a prefix (e.g. `aws___search_documentation`).

# Workflow steering (load only what you need)
- Choosing a service or feature, or answering "what's new" -> `new-features-check.md`
- Regions, limits, ARNs, best practices during design -> `aws-workflow.md`

# Behaviour rules
1. Never rely on memory for the existence of services and features, regional availability, limits or ARN
   formats: check with the tools.
2. Always cite the source: page URL and, for announcements, the publication date.
3. If the server is not reachable, finds nothing or hits rate limits, **stop and report it**; do not fall back
   on remembered values and do not present them as verified.
4. The server cannot see your AWS account: quotas you find are the documented **default** values, not those
   applied to the account. Say so when you use them.
