"""
ForgeResult - 骨架处理结果数据类

标准化的处理结果，包含成功状态、错误信息和处理数据。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ForgeResult:
    """
    骨架处理结果数据类

    标准化的处理结果，包含成功状态、错误信息和处理数据。
    """

    project: Optional[Dict] = None
    patterns: List[Dict] = field(default_factory=list)
    mental_models: List[Dict] = field(default_factory=list)
    tech_knowledge: List[Dict] = field(default_factory=list)
    success: bool = False
    errors: List[Dict] = field(default_factory=list)

    # 解析元数据
    parse_metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "project": self.project,
            "patterns": self.patterns,
            "mental_models": self.mental_models,
            "tech_knowledge": self.tech_knowledge,
            "success": self.success,
            "errors": self.errors,
            "parse_metadata": self.parse_metadata
        }