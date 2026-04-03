# MCP Server — Search Atlas

Connect [Search Atlas](https://searchatlas.com) to Claude via the Model Context Protocol (MCP).

## Tools available

| Tool | Description |
|---|---|
| `keyword_research` | Search volume, difficulty, CPC for any keyword |
| `get_backlinks` | Backlink data for a domain or URL |
| `site_audit` | Technical SEO audit for a domain |
| `rank_tracker` | Current ranking positions for keywords |
| `competitor_analysis` | Top keywords and traffic for a competitor |
| `content_optimizer` | On-page SEO recommendations |
| `knowledge_graph` | Entity data from the knowledge graph |

---

## Setup

### 1. Install dependencies

```bash
cd mcp_searchatlas
pip install -e .
```

### 2. Get your Search Atlas API key

Log in to [searchatlas.com](https://searchatlas.com), go to **Settings → API**, and copy your API key.

### 3. Configure Claude Desktop

Open your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the following block inside `"mcpServers"`:

```json
{
  "mcpServers": {
    "searchatlas": {
      "command": "mcp-searchatlas",
      "env": {
        "SEARCHATLAS_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

If `mcp-searchatlas` is not on your PATH, use the full path to the script instead:

```json
{
  "mcpServers": {
    "searchatlas": {
      "command": "python",
      "args": ["-m", "mcp_searchatlas.server"],
      "env": {
        "SEARCHATLAS_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After saving the config, restart Claude Desktop. You should see **searchatlas** appear as a connected MCP server.

---

## Usage examples

Once connected, you can ask Claude things like:

- *"Research the keyword 'best running shoes' for the US market"*
- *"Get backlinks for nike.com"*
- *"Run a site audit on mywebsite.com"*
- *"Track rankings for example.com for the keywords 'seo tools' and 'keyword research'"*
- *"Analyse the competitor domain ahrefs.com"*
- *"Optimise my content targeting the keyword 'content marketing'"*
