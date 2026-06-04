# Maintenance Scripts

These are **developer tools** for maintaining the project.
Agents should NOT invoke these directly.

## generate_tool_registry.py

Parses Python source files and generates structured tool registry definitions for LLM function calling.

**Usage:**
```bash
# Single file
python scripts/generate_tool_registry.py src/tools_singlecell/preprocessing.py

# All files in a directory
for file in src/tools_singlecell/*.py; do
  python scripts/generate_tool_registry.py "$file"
done
```

**Outputs:**
- `src/tool_registry/<module>_<filename>.py` (e.g., `singlecell_preprocessing.py`)

**When to run:**
- After adding new tool functions
- After updating tool docstrings
- Use `/generate-tool-registry` Claude command for convenience

## generate_mcp_server.py

Generates an MCP (Model Context Protocol) server that exposes tools from the tool registry to Claude subagents and other MCP-compatible AI systems.

**Usage:**
```bash
# Generate one server per category (recommended for Claude agents)
# This allows granular tool selection when configuring agents
python scripts/generate_mcp_server.py --all-categories

# Generate server for ALL 428 tools (single server)
python scripts/generate_mcp_server.py

# Generate server for specific categories only
python scripts/generate_mcp_server.py --categories external_literature,external_genomics

# List available categories
python scripts/generate_mcp_server.py --list-categories
```

**Outputs:**
- `--all-categories`: Creates 29 servers in `src/mcp_servers/` (e.g., `literature.py`, `genomics.py`)
- Default: Creates `mcp_server.py` at project root

**After generation:**
1. Install MCP dependencies: `pip install -r requirements-mcp.txt`
2. Add the MCP server(s) to Claude settings (see output from script)

**When to run:**
- After adding new tools to the registry
- When you want to expose tools to Claude subagents
- Use `--all-categories` for granular control over which tools each agent can access

## generate_cookbooks.py

Regenerates cookbook.md files in skill directories.

**Usage:**
```bash
python scripts/generate_cookbooks.py --skill scRNA-feature-selection
# Or all skills:
python scripts/generate_cookbooks.py --all
```

**Outputs:**
- `.claude/skills/*/cookbook.md`

**When to run:**
- After documentation updates
- When tool parameters change
- After generate_tool_registry.py

## sync_documentation.py

Syncs everything at once.

**Usage:**
```bash
python scripts/sync_documentation.py
```

**What it does:**
1. Runs generate_tool_registry.py
2. Runs generate_cookbooks.py
3. Validates all references
4. Generates summary report
