"""
KnowledgeForge 骨架模块

核心组件：
- KnowledgeForgePipeline: 主流程骨架
- ForgeResult: 处理结果数据类
- ExtractionConfidence: 置信度枚举
- ExtractionEvidence: 证据记录类
- 契约基类: 所有扩展点的抽象基类

骨架原则：
1. 流程控制不变
2. 扩展点可拔插
3. 失败降级
4. 结果标准化
"""

from knowledgeforge.skeleton.pipeline import KnowledgeForgePipeline
from knowledgeforge.skeleton.result import ForgeResult
from knowledgeforge.skeleton.confidence import ExtractionConfidence
from knowledgeforge.skeleton.evidence import ExtractionEvidence
from knowledgeforge.skeleton.contracts import (
    ParserContract,
    PatternExtractorContract,
    MentalExtractorContract,
    TechExtractorContract,
    StorageContract,
    VisualizerContract,
    IndexerContract,
    QueryContract,
    CacheManagerContract,
)

__all__ = [
    "KnowledgeForgePipeline",
    "ForgeResult",
    "ExtractionConfidence",
    "ExtractionEvidence",
    "ParserContract",
    "PatternExtractorContract",
    "MentalExtractorContract",
    "TechExtractorContract",
    "StorageContract",
    "VisualizerContract",
    "IndexerContract",
    "QueryContract",
    "CacheManagerContract",
]