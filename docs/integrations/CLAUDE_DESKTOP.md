# Stele in Claude Desktop (via MCP)

Edit `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Hosted (recommended — core ledger)

```json
{
  "mcpServers": {
    "stele": {
      "url": "https://stele.leocelis.com/core/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

Full research library: use `https://stele.leocelis.com/sse` instead.

Restart Claude Desktop. Tools appear in the MCP panel.
