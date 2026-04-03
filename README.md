# FitSearch AI MCP Server

A comprehensive Model Context Protocol (MCP) server for fitness research with live web search, deep research capabilities, and verified source verification.

## Features

### MCP Tools
- **web_search**: Search the web for fitness/health topics with source verification
- **deep_research**: Comprehensive research with verified sources, key findings, benefits, risks
- **intent_detection**: Classify user query intent (supplement, diet, workout, compound, medical)
- **verify_source**: Check if a URL is from a trusted domain

### Source Verification
Trusted domains include:
- **Scientific**: PubMed, NCBI, NIH, WHO, CDC
- **Medical**: Mayo Clinic, Cleveland Clinic, WebMD
- **Fitness**: Examine.com, Bodybuilding.com
- **Journals**: Nature, ScienceDirect, Springer, JISSN

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/web_search` | GET/POST | MCP tool for web search |
| `/mcp/deep_research` | GET/POST | MCP tool for deep research |
| `/mcp/intent` | GET/POST | MCP tool for intent detection |
| `/mcp/verify` | GET/POST | MCP tool for source verification |
| `/mcp/trusted-domains` | GET | List all trusted domains |
| `/search` | GET/POST | Standard search endpoint |
| `/deep-research` | GET/POST | Deep research endpoint |
| `/intent` | GET/POST | Intent detection endpoint |
| `/health` | GET | Health check |

## Environment Variables

```
ZENSERP_API_KEY=your_zenserp_api_key
ANTHROPIC_API_KEY=your_anthropic_key (optional)
PUBMED_API_KEY=your_pubmed_key (optional)
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export ZENSERP_API_KEY=your_key
```

3. Run the server:
```bash
python mcp_server.py
```

4. Open browser: `http://localhost:5000`

## MCP Client Integration

Example Python client using the MCP SDK:

```python
from mcp.client import MCPClient

async def main():
    client = MCPClient("http://your-server.com:5000")
    
    # Web search
    result = await client.call_tool("web_search", {
        "query": "creatine monohydrate benefits",
        "max_results": 10
    })
    print(result)
    
    # Deep research
    result = await client.call_tool("deep_research", {
        "query": "testosterone replacement therapy"
    })
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Response Format

### Web Search Response
```json
{
  "tool": "web_search",
  "query": "creatine benefits",
  "results": {
    "results": [...],
    "verified_results": [...],
    "total_results": 10,
    "verified_count": 5
  },
  "intent": {
    "primary_intent": "supplement",
    "confidence": 0.85,
    "category": "supplements"
  }
}
```

### Deep Research Response
```json
{
  "tool": "deep_research",
  "query": "anavar cycle",
  "research": {
    "summary": "...",
    "key_findings": [...],
    "benefits": [...],
    "risks": [...],
    "verified_sources": [...],
    "references": [...],
    "source_stats": {
      "verified": 12,
      "scientific": 5,
      "general": 3
    }
  }
}
```

## Deployment

Deploy to Render:

1. Push to GitHub
2. Connect to Render
3. Add environment variables:
   - `ZENSERP_API_KEY`
   - `ANTHROPIC_API_KEY` (optional)
   - `PUBMED_API_KEY` (optional)
4. Deploy

## License

MIT
