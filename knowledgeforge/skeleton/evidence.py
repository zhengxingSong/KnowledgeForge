"""
证据记录模块

每个推断必须记录证据，支持用户审查。
参考 graphify 的证据链设计。
"""

from dataclasses import dataclass, field
from typing import Dict, List

from knowledgeforge.skeleton.confidence import ExtractionConfidence


@dataclass
class ExtractionEvidence:
    """
    提取证据记录

    每个推断必须记录证据，支持用户审查。
    参考 graphify 的证据链设计。
    """

    # 置信度
    confidence: ExtractionConfidence

    # 推断理由
    reasoning: str

    # 证据字段
    structural_match: bool = False
    naming_hints: List[str] = field(default_factory=list)
    doc_hints: List[str] = field(default_factory=list)
    tests_verified: bool = False
    test_coverage: float = 0.0

    # 决策详情
    decision_threshold: float = 0.0
    alternative_candidates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "confidence": self.confidence.value,
            "reasoning": self.reasoning,
            "structural_match": self.structural_match,
            "naming_hints": self.naming_hints,
            "doc_hints": self.doc_hints,
            "tests_verified": self.tests_verified,
            "test_coverage": self.test_coverage,
            "decision_threshold": self.decision_threshold,
            "alternative_candidates": self.alternative_candidates
        }

    @classmethod
    def static(cls, reasoning: str) -> "ExtractionEvidence":
        """创建静态提取证据"""
        return cls(
            confidence=ExtractionConfidence.EXTRACTED_STATIC,
            reasoning=reasoning
        )

    @classmethod
    def inferred_pattern(
        cls,
        reasoning: str,
        naming_hints: List[str] = None,
        structural_match: bool = True
    ) -> "ExtractionEvidence":
        """创建模式推断证据"""
        return cls(
            confidence=ExtractionConfidence.INFERRED_PATTERN,
            reasoning=reasoning,
            naming_hints=naming_hints or [],
            structural_match=structural_match
        )

    @classmethod
    def inferred_semantic(
        cls,
        reasoning: str,
        doc_hints: List[str] = None
    ) -> "ExtractionEvidence":
        """创建语义推断证据"""
        return cls(
            confidence=ExtractionConfidence.INFERRED_SEMANTIC,
            reasoning=reasoning,
            doc_hints=doc_hints or []
        )