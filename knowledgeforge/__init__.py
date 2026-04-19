"""
KnowledgeForge - 开源项目知识锻造系统

从开源项目中提取设计模式和心智模型，形成可复用的知识库。

主要模块：
- skeleton: 核心骨架（Pipeline、契约基类、置信度系统）
- defaults: 默认实现（Parser、Extractor、Storage）
- cli: 命令行工具
- mcp: MCP服务器（AI助手集成）

使用方式：
    from knowledgeforge import KnowledgeForgePipeline

    pipeline = KnowledgeForgePipeline()
    result = pipeline.forge(Path("/path/to/project"))
"""

__version__ = "0.0.1"
__author__ = "KnowledgeForge Team"

from knowledgeforge.skeleton import (
    KnowledgeForgePipeline,
    ForgeResult,
    ExtractionConfidence,
    ExtractionEvidence,
)

__all__ = [
    "KnowledgeForgePipeline",
    "ForgeResult",
    "ExtractionConfidence",
    "ExtractionEvidence",
]