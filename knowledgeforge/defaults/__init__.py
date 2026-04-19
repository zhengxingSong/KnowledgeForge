"""
KnowledgeForge 默认实现模块

Phase 0 默认实现：
- DefaultParser: 项目结构解析（基础版）
- DefaultPatternExtractor: 设计模式提取
- DefaultMentalExtractor: 心智模型提取
- LocalStorage: 本地文件存储
- JSONIndexer: JSON索引管理

Phase 1 新增：
- LanguageConfig: 23+语言配置
- TreeSitterParser: tree-sitter AST解析
- CacheManager: SHA256缓存管理
"""

from knowledgeforge.defaults.parser import DefaultParser
from knowledgeforge.defaults.pattern_extractor import DefaultPatternExtractor
from knowledgeforge.defaults.mental_extractor import DefaultMentalExtractor
from knowledgeforge.defaults.storage import LocalStorage
from knowledgeforge.defaults.indexer import JSONIndexer

# Phase 1 新增
from knowledgeforge.defaults.language_config import LanguageConfig, get_language_config
from knowledgeforge.defaults.tree_sitter_parser import TreeSitterParser
from knowledgeforge.defaults.cache_manager import CacheManager, get_cache_manager

__all__ = [
    # Phase 0
    "DefaultParser",
    "DefaultPatternExtractor",
    "DefaultMentalExtractor",
    "LocalStorage",
    "JSONIndexer",
    # Phase 1
    "LanguageConfig",
    "get_language_config",
    "TreeSitterParser",
    "CacheManager",
    "get_cache_manager",
]