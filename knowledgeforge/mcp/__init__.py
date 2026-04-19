"""
KnowledgeForge MCP模块

MCP服务器实现，用于AI编码助手集成。

支持平台：
- Claude Desktop
- Cursor IDE
- Codex
- Windsurf

Phase 2 功能：
- MCP服务器协议
- forge_project工具
- query_patterns工具
- blast_radius工具
- get_evidence工具
"""

from knowledgeforge.mcp.server import (
    KnowledgeForgeMCPServer,
    create_mcp_server,
    run_mcp_server
)

__all__ = [
    "KnowledgeForgeMCPServer",
    "create_mcp_server",
    "run_mcp_server",
]