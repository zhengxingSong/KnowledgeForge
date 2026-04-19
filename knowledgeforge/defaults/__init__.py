"""
KnowledgeForge 默认实现模块

默认实现：
- DefaultParser: 项目结构解析（Phase 0 基础版）
- DefaultPatternExtractor: 设计模式提取
- DefaultMentalExtractor: 心智模型提取
- LocalStorage: 本地文件存储
- JSONIndexer: JSON索引管理
"""

from knowledgeforge.defaults.parser import DefaultParser
from knowledgeforge.defaults.pattern_extractor import DefaultPatternExtractor
from knowledgeforge.defaults.mental_extractor import DefaultMentalExtractor
from knowledgeforge.defaults.storage import LocalStorage
from knowledgeforge.defaults.indexer import JSONIndexer

__all__ = [
    "DefaultParser",
    "DefaultPatternExtractor",
    "DefaultMentalExtractor",
    "LocalStorage",
    "JSONIndexer",
]