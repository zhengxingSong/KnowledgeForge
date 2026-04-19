"""
KnowledgeForge CLI模块

命令行工具入口，提供forge、query、list等命令。

设计原则：
- 薄壳设计：CLI只负责交互，不实现逻辑
- 命令清晰：每个命令职责单一
- 参数简洁：用户能用最少的参数完成任务
"""

from knowledgeforge.cli.main import main

__all__ = ["main"]