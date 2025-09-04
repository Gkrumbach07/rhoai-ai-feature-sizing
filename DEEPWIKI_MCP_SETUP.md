# DeepWiki MCP Server Integration Guide

This guide explains how to set up and use the DeepWiki MCP (Model Context Protocol) server integration for enhanced agent research capabilities.

## Overview

The DeepWiki MCP integration allows your agents to conduct real-time research on GitHub repositories, providing:

- **Repository Structure Analysis**: Understand project organization and documentation
- **Content Retrieval**: Access repository documentation and wikis
- **AI-Powered Q&A**: Ask specific questions about repositories and get contextual answers
- **Enhanced Agent Analysis**: Agents can use research findings to provide better RFE analysis

## Quick Setup

### 1. Environment Configuration

Copy the environment template and configure MCP settings:

```bash
cp env.template .env
```

Edit `.env` and configure the MCP section:

```env
# DeepWiki MCP Configuration
ENABLE_DEEPWIKI_MCP=true
DEEPWIKI_MCP_URL=https://mcp.deepwiki.com/sse
DEEPWIKI_MCP_PROTOCOL=sse
DEEPWIKI_MCP_TIMEOUT=30
DEEPWIKI_MCP_MAX_RETRIES=3

# Optional: Default repositories for research
MCP_DEFAULT_REPOS=https://github.com/kubeflow/kubeflow,https://github.com/kserve/kserve
```

### 2. Initialize Settings with MCP

In your Python code, initialize settings with MCP enabled:

```python
from src.settings import init_settings

# Enable MCP during initialization
init_settings(enable_mcp=True)
```

### 3. Test the Integration

Run the example script to verify everything works:

```bash
python src/deepwiki_mcp_integration.py
```

## Configuration Options

### MCP Server Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENABLE_DEEPWIKI_MCP` | `true` | Enable/disable MCP integration |
| `DEEPWIKI_MCP_URL` | `https://mcp.deepwiki.com/sse` | MCP server endpoint |
| `DEEPWIKI_MCP_PROTOCOL` | `sse` | Protocol (`sse` or `mcp`) |
| `DEEPWIKI_MCP_TIMEOUT` | `30` | Request timeout in seconds |
| `DEEPWIKI_MCP_MAX_RETRIES` | `3` | Maximum retry attempts |

### Protocol Options

- **SSE (Server-Sent Events)**: `https://mcp.deepwiki.com/sse` (Recommended)
- **Streamable HTTP**: `https://mcp.deepwiki.com/mcp` (Alternative)

Choose SSE for maximum compatibility.

## Usage Examples

### Basic MCP Operations

```python
from src.mcp_client import quick_research, get_repo_overview

# Quick question about a repository
answer = await quick_research(
    "https://github.com/kubeflow/kubeflow",
    "How does Kubeflow handle model serving?"
)

# Get repository overview
overview = await get_repo_overview("https://github.com/kubeflow/kubeflow")
```

### Enhanced Agent Analysis

```python
from src.agents import RFEAgentManager
from src.settings import init_settings

# Initialize with MCP enabled
init_settings(enable_mcp=True)
manager = RFEAgentManager()

# Specify research repositories for the analysis
research_repos = [
    "https://github.com/kubeflow/kubeflow",
    "https://github.com/mlflow/mlflow"
]

# Run enhanced analysis
async for event in manager.analyze_rfe_streaming(
    "RESEARCH_SPECIALIST",
    "Implement model versioning system",
    manager.agent_configs["RESEARCH_SPECIALIST"],
    research_repos
):
    if event["type"] == "research_completed":
        research_data = event["research_data"]
        # Process research results
    elif event["type"] == "complete":
        analysis_result = event["result"]
        # Process final analysis
```

### Custom Research Service

```python
from src.mcp_client import MCPResearchService, get_mcp_config

config = get_mcp_config()
research_service = MCPResearchService(config)

# Multi-repository research
results = await research_service.research_repositories(
    ["https://github.com/ray-project/ray"],
    ["How is distributed training implemented?"]
)

# Focused research for specific agent
focused_results = await research_service.focused_research(
    "https://github.com/kubeflow/kubeflow",
    "STAFF_ENGINEER",
    "Add GPU scheduling optimization"
)
```

## Available Agents with MCP Support

### Research Specialist (`RESEARCH_SPECIALIST`)
- **Purpose**: Specialized in technology research and repository analysis
- **MCP Features**: Enabled by default
- **Research Focus**: Implementation patterns, best practices, competitive analysis
- **Default Repos**: Kubeflow, KServe, OpenDataHub, Ray, PyTorch, TensorFlow

### Existing Agents Enhanced
All existing agents can use MCP research by setting `enable_mcp_research: true` in their configuration:

- **Staff Engineer**: Technical implementation research
- **Engineering Manager**: Process and team coordination research  
- **UX Architect**: Interface and user experience pattern research

## MCP Tools Available

### `read_wiki_structure`
Get documentation structure for a repository:
```python
structure = await client.read_wiki_structure("https://github.com/user/repo")
```

### `read_wiki_contents`
Retrieve documentation content:
```python
content = await client.read_wiki_contents(
    "https://github.com/user/repo",
    topic="installation"  # optional
)
```

### `ask_question`
AI-powered repository Q&A:
```python
answer = await client.ask_question(
    "https://github.com/user/repo",
    "How do I deploy this system?"
)
```

## Fallback Support ⭐

**NEW**: The MCP integration now includes robust fallback support for when the DeepWiki server is unavailable.

### Fallback Modes

| Mode | Environment Variable | Behavior |
|------|---------------------|----------|
| **Production** | `DEEPWIKI_MCP_FALLBACK=true` | Try MCP server first, use fallback if unavailable |
| **Demo** | `DEEPWIKI_MCP_DEMO_MODE=true` | Always use demo responses (for testing) |
| **Disabled** | `ENABLE_DEEPWIKI_MCP=false` | Completely disable MCP features |

### Benefits

- ✅ **No service disruption** when external MCP server is down
- ✅ **Consistent API** regardless of server availability  
- ✅ **Development friendly** with meaningful demo responses
- ✅ **Enterprise ready** for restricted network environments

## Troubleshooting

### MCP Server Unavailable (HTTP 404)

**This is normal!** The integration includes fallback support.

```env
# Enable fallback responses (recommended)
DEEPWIKI_MCP_FALLBACK=true

# For testing/demo purposes
DEEPWIKI_MCP_DEMO_MODE=true
```

When the MCP server returns 404 errors, the system automatically:

1. **Detects server unavailability**
2. **Switches to fallback mode**
3. **Provides demo responses** that maintain agent functionality
4. **Logs warnings** (not errors) for transparency

### Common Issues

#### "MCP research unavailable"
- Check that `ENABLE_DEEPWIKI_MCP=true` in your `.env`
- Verify `init_settings(enable_mcp=True)` is called
- Review fallback configuration settings

#### Connection Timeouts
- Increase `DEEPWIKI_MCP_TIMEOUT` value
- Check your internet connection
- Enable `DEEPWIKI_MCP_FALLBACK=true` for graceful handling

#### Research Failures
- Enable fallback mode: `DEEPWIKI_MCP_FALLBACK=true`
- Use demo mode for testing: `DEEPWIKI_MCP_DEMO_MODE=true`
- Check logs for specific error details

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('src.mcp_client').setLevel(logging.DEBUG)
```

## Advanced Configuration

### Custom Research Repositories

Set default research repositories per agent:

```yaml
# agents/custom_agent.yaml
default_research_repos:
  - "https://github.com/custom/repo1"
  - "https://github.com/custom/repo2"
```

### Agent-Specific Research Questions

Customize research questions for different agent personas by modifying `focused_research()` in `mcp_client.py`.

### Caching Research Results

For production use, consider implementing caching:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_research(repo_url, question):
    return await quick_research(repo_url, question)
```

## Performance Considerations

- **Parallel Research**: The system conducts research on multiple repositories in parallel
- **Timeout Management**: Configurable timeouts prevent long waits
- **Retry Logic**: Automatic retries with exponential backoff
- **Context Limits**: Research results are summarized to fit within LLM context limits

## Security Notes

- DeepWiki MCP server is a **public service** - no authentication required for public repos
- **Private repositories** require Devin account setup (see [DeepWiki MCP docs](https://docs.devin.ai/work-with-devin/deepwiki-mcp))
- Research data is processed by external AI services - review data handling policies
- Repository URLs are sent to the MCP server - ensure compliance with your organization's policies

## Next Steps

1. **Test Integration**: Run the example script to verify setup
2. **Customize Agents**: Add MCP research to your existing agents
3. **Create Research Workflows**: Build custom research processes for your use cases
4. **Monitor Performance**: Track research quality and adjust repositories as needed

For more advanced usage and customization options, see the source code in `src/mcp_client.py` and `src/agents.py`.
