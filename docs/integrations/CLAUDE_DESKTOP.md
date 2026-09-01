# Stele in Claude Desktop (via MCP)

Edit `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Hosted (recommended)

```json
{
  "mcpServers": {
    "stele": {
      "url": "https://stele.leocelis.com/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

Restart Claude Desktop. Tools appear in the MCP panel.
