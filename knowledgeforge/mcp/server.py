"""
KnowledgeForge MCP Server

MCP (Model Context Protocol) server implementation for AI assistant integration.
Supports Claude Desktop, Cursor IDE, Windsurf and other MCP-compatible tools.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None
    Tool = None
    TextContent = None

from knowledgeforge.skeleton.pipeline import KnowledgeForgePipeline
from knowledgeforge.defaults.storage import LocalStorage
from knowledgeforge.defaults.indexer import JSONIndexer


class KnowledgeForgeMCPServer:
    """
    KnowledgeForge MCP Server

    Exposes KnowledgeForge functionality as MCP tools:
    - forge_project: Parse a project and extract knowledge
    - query_patterns: Search patterns in knowledge base
    - blast_radius: Analyze pattern impact/dependencies
    - get_evidence: Get evidence details for a pattern
    - list_projects: List all parsed projects
    """

    SERVER_NAME = "knowledgeforge"
    SERVER_VERSION = "0.2.0"

    # Tool definitions
    TOOLS = [
        {
            "name": "forge_project",
            "description": "Parse a code project and extract design patterns, mental models, and structure. Returns structured knowledge.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory to parse"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["full", "incremental"],
                        "default": "full",
                        "description": "Parse mode: full (re-parse all) or incremental (use cache)"
                    }
                },
                "required": ["project_path"]
            }
        },
        {
            "name": "query_patterns",
            "description": "Search for design patterns in the knowledge base by keyword or pattern name.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (pattern name, keyword, or concept)"
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional: filter to specific project"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum results to return"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "blast_radius",
            "description": "Analyze the impact radius of a pattern - which modules, functions, and patterns are affected by changes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern ID to analyze (e.g., 'P-001')"
                    },
                    "depth": {
                        "type": "integer",
                        "default": 3,
                        "description": "Analysis depth (1-5)"
                    }
                },
                "required": ["pattern_id"]
            }
        },
        {
            "name": "get_evidence",
            "description": "Get detailed evidence for a pattern extraction - why it was detected and what confidence level.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern ID to get evidence for"
                    }
                },
                "required": ["pattern_id"]
            }
        },
        {
            "name": "list_projects",
            "description": "List all projects that have been parsed and stored in the knowledge base.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_pattern_detail",
            "description": "Get full details of a specific pattern including code template and application guidance.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern ID to get details for"
                    }
                },
                "required": ["pattern_id"]
            }
        }
    ]

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize MCP server

        Args:
            output_dir: Directory for knowledge output
        """
        self.pipeline = KnowledgeForgePipeline()
        output_dir_str = str(output_dir) if output_dir else None
        self.storage = LocalStorage(output_dir=output_dir_str)
        self.indexer = JSONIndexer()

        # MCP Server instance
        self.server: Optional[Server] = None

    def start(self) -> bool:
        """
        Start MCP server

        Returns:
            bool: Success status
        """
        if not MCP_AVAILABLE:
            print("[MCP] MCP library not available. Install with: pip install mcp")
            return False

        try:
            self.server = Server(self.SERVER_NAME)

            # Register tools
            self._register_tools()

            return True
        except Exception as e:
            print(f"[MCP] Failed to start server: {e}")
            return False

    def _register_tools(self) -> None:
        """Register all MCP tools"""
        if not self.server:
            return

        # Register tool definitions
        for tool_def in self.TOOLS:
            tool = Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                inputSchema=tool_def["inputSchema"]
            )
            self.server.add_tool(tool)

        # Set tool handler
        self.server.set_tool_handler(self._handle_tool_call)

    def _handle_tool_call(self, name: str, arguments: Dict) -> List[TextContent]:
        """
        Handle MCP tool call

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            List[TextContent]: Response content
        """
        try:
            result = self._execute_tool(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        except Exception as e:
            error_result = {"error": str(e), "tool": name}
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    def _execute_tool(self, name: str, arguments: Dict) -> Dict:
        """
        Execute tool logic

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Dict: Tool result
        """
        if name == "forge_project":
            return self._forge_project(arguments)

        elif name == "query_patterns":
            return self._query_patterns(arguments)

        elif name == "blast_radius":
            return self._blast_radius(arguments)

        elif name == "get_evidence":
            return self._get_evidence(arguments)

        elif name == "list_projects":
            return self._list_projects()

        elif name == "get_pattern_detail":
            return self._get_pattern_detail(arguments)

        else:
            return {"error": f"Unknown tool: {name}"}

    def _forge_project(self, arguments: Dict) -> Dict:
        """Execute forge_project tool"""
        project_path = Path(arguments.get("project_path"))
        mode = arguments.get("mode", "full")

        if not project_path.exists():
            return {"error": f"Project path does not exist: {project_path}"}

        # Run forge
        result = self.pipeline.forge(project_path)

        return {
            "success": result.success,
            "project": result.project,
            "patterns_count": len(result.patterns),
            "mental_models_count": len(result.mental_models),
            "patterns": result.patterns[:5],  # Return first 5 patterns
            "mental_models": result.mental_models[:5],  # Return first 5 mental models
            "errors": result.errors
        }

    def _query_patterns(self, arguments: Dict) -> Dict:
        """Execute query_patterns tool"""
        query = arguments.get("query", "")
        project_filter = arguments.get("project")
        limit = arguments.get("limit", 10)

        # Search in index
        results = self.indexer.search(query)

        # Filter by project if specified
        if project_filter:
            results = [r for r in results if r.get("project") == project_filter]

        # Limit results
        results = results[:limit]

        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }

    def _blast_radius(self, arguments: Dict) -> Dict:
        """Execute blast_radius tool"""
        pattern_id = arguments.get("pattern_id")
        depth = arguments.get("depth", 3)

        # Load pattern data
        pattern = self._find_pattern(pattern_id)
        if not pattern:
            return {"error": f"Pattern not found: {pattern_id}"}

        # Analyze dependencies (Phase 2 implementation)
        analysis = {
            "pattern_id": pattern_id,
            "pattern_name": pattern.get("name"),
            "depth": depth,
            "affected_modules": [],
            "related_patterns": [],
            "dependencies": [],
            "confidence": pattern.get("confidence"),
            "message": "Blast-radius analysis - Phase 2 feature"
        }

        return analysis

    def _get_evidence(self, arguments: Dict) -> Dict:
        """Execute get_evidence tool"""
        pattern_id = arguments.get("pattern_id")

        pattern = self._find_pattern(pattern_id)
        if not pattern:
            return {"error": f"Pattern not found: {pattern_id}"}

        evidence = pattern.get("evidence", {})

        return {
            "pattern_id": pattern_id,
            "pattern_name": pattern.get("name"),
            "confidence": pattern.get("confidence"),
            "evidence": evidence
        }

    def _list_projects(self) -> Dict:
        """Execute list_projects tool"""
        projects = self.indexer.list_projects()

        return {
            "projects_count": len(projects),
            "projects": projects
        }

    def _get_pattern_detail(self, arguments: Dict) -> Dict:
        """Execute get_pattern_detail tool"""
        pattern_id = arguments.get("pattern_id")

        pattern = self._find_pattern(pattern_id)
        if not pattern:
            return {"error": f"Pattern not found: {pattern_id}"}

        return {
            "pattern": pattern
        }

    def _find_pattern(self, pattern_id: str) -> Optional[Dict]:
        """Find pattern by ID"""
        index_data = self.indexer.load_index()

        if not index_data:
            return None

        # 直接从 patterns dict 查找
        patterns = index_data.get("patterns", {})
        if pattern_id in patterns:
            return patterns[pattern_id]

        return None

    def generate_config(self, output_path: Optional[Path] = None) -> Dict:
        """
        Generate MCP configuration for Claude Desktop/Cursor

        Args:
            output_path: Path to save config file

        Returns:
            Dict: Configuration dict
        """
        config = {
            "mcpServers": {
                "knowledgeforge": {
                    "command": "python",
                    "args": ["-m", "knowledgeforge.mcp.server"],
                    "env": {}
                }
            }
        }

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

        return config

    def run_stdio(self) -> None:
        """Run MCP server using stdio transport"""
        if not self.server:
            print("[MCP] Server not initialized")
            return

        self.server.run_stdio()


def create_mcp_server() -> KnowledgeForgeMCPServer:
    """Factory function to create MCP server"""
    return KnowledgeForgeMCPServer()


def run_mcp_server() -> None:
    """Entry point to run MCP server"""
    server = create_mcp_server()
    if server.start():
        server.run_stdio()


if __name__ == '__main__':
    run_mcp_server()