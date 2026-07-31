**Agent: Jira Ticket Data Extraction**

Description: Fetches a Jira ticket by key (issue code), normalizes the data into a stable JSON shape, and returns it. This agent is intended to use the workspace's Atlassian MCP tools (the `mcp_atlassian-mcp_*` functions) rather than local helper scripts.

Inputs:
- `issueKey` (string): Jira issue key, e.g. `PROJ-123`.

Outputs:
- JSON object with the normalized shape (see example below).

Configuration / Authentication:
- For the MCP functions you typically provide a `cloudId` (or let the MCP tool infer it from your session). When calling Jira directly via an HTTP helper you still need `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`.

How it works:
- The agent should call the appropriate MCP function, for example `mcp_atlassian-mcp_getJiraIssue`, passing `cloudId` and `issueIdOrKey`.
- If the MCP tool returns a wrapped payload the agent should unwrap `data`/`result`/`issue` keys and then normalize the `fields` payload into the canonical shape shown below.
- Field extraction: `key`, `fields.summary`, `fields.description` (or rendered fields),`fields.issuetype.name`, `fields.priority.name`, `fields.project.key`, 
  `fields.project.name`, `fields.components` (liste de noms), `fields.status.name`, `fields.reporter`, `fields.assignee`, `fields.labels`, `fields.created`, `fields.updated`, `fields.comment.comments`.
- Description parsing: 
  - The Jira description typically follows a Markdown-like structure with 
  headers such as "### Background", "### Scope", and "### Acceptance Criteria",
  each followed by a bullet list (lines starting with "*").
  - Parse the raw description into these sections:
    - `background`: the paragraph(s) under "### Background" (if the header 
    is absent, use the first paragraph before any header as background)
    - `scope`: each bullet point under "### Scope" as a separate array item
    - `acceptanceCriteria`: each bullet point under "### Acceptance Criteria" 
    as a separate array item
  - If a section header is missing entirely, return an empty array/string 
  for that field rather than guessing its content.
  - Always keep `descriptionRaw` as the complete, unmodified original text, 
  regardless of parsing success.

Normalization example:

{
  "key": "PROJ-123",
  "summary": "Short summary",
  "issueType": "Feature",
  "priority": "High",
  "project": { "key": "PROJ", "name": "Project Name" },
  "status": "In Progress",
  "reporter": { "name": "Alice", "accountId": "..." },
  "assignee": { "name": "Bob", "accountId": "..." },
  "labels": ["backend","urgent"],
  "components": ["Backend", "Authentication"],
  "created": "2026-07-14T12:34:56.000Z",
  "updated": "2026-07-15T08:12:00.000Z",
  "descriptionRaw": "Full raw description text as returned by Jira (text or HTML)",
  "background": "Extracted from the '### Background' section of the description, if present",
  "scope": [
    "Extracted from the '### Scope' bullet list in the description, if present"
  ],
  "acceptanceCriteria": [
    "Extracted from the '### Acceptance Criteria' bullet list in the description, if present"
  ],
  "comments": [ { "author": "Someone", "body": "...", "created": "..." }, ... ]
}

Example MCP function call (pseudo):

```
// call the MCP function: mcp_atlassian-mcp_getJiraIssue
{ "cloudId": "your-site.atlassian.net", "issueIdOrKey": "PROJ-123" }
```

Example normalized output:

{
  "key": "PROJ-123",
  "summary": "Short summary",
  "issueType": "Feature",
  "priority": "High",
  "project": { "key": "PROJ", "name": "Project Name" },
  "status": "In Progress",
  "reporter": { "name": "Alice", "accountId": "..." },
  "assignee": { "name": "Bob", "accountId": "..." },
  "labels": ["backend","urgent"],
  "components": ["Backend", "Authentication"],
  "created": "2026-07-14T12:34:56.000Z",
  "updated": "2026-07-15T08:12:00.000Z",
  "descriptionRaw": "Full raw description text as returned by Jira (text or HTML)",
  "background": "Extracted from the '### Background' section of the description, if present",
  "scope": [
    "Extracted from the '### Scope' bullet list in the description, if present"
  ],
  "acceptanceCriteria": [
    "Extracted from the '### Acceptance Criteria' bullet list in the description, if present"
  ],
  "comments": [ { "author": "Someone", "body": "...", "created": "..." }, ... ]
}

Notes:
- Use `mcp_atlassian-mcp_getJiraIssue` to retrieve a specific issue. Use `mcp_atlassian-mcp_search` or `mcp_atlassian-mcp_search`-style tools to find issues by JQL.
- When invoking from an agent, prefer the built-in MCP functions so secrets and authentication are handled by the MCP integration.

Next steps:
- I can update this agent doc to include a concrete example using the workspace's MCP tooling and add a small wrapper that calls `mcp_atlassian-mcp_getJiraIssue` then normalizes the result. Would you like that?
