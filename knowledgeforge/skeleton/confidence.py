"""
置信度定义模块

参考 graphify 的置信度标注系统，支持5级置信度。
"""

from enum import Enum


class ExtractionConfidence(Enum):
    """
    知识提取置信度枚举

    参考 graphify 的置信度标注系统，支持5级置信度。
    """

    # Layer 0: 静态解析
    EXTRACTED_STATIC = "extracted_static"
    """
    tree-sitter 直接提取
    特点：100%确定、确定性解析
    示例：函数名、类名、import语句
    """

    # Layer 1: 静态推断
    INFERRED_PATTERN = "inferred_pattern"
    """
    结构模式匹配推断
    特点：基于结构特征、需验证
    示例：工厂模式（类名含Factory + create方法）
    """

    INFERRED_SEMANTIC = "inferred_semantic"
    """
    LLM语义推断
    特点：基于命名/文档语义、需验证
    示例：心智模型推断（Pipeline心智模型）
    """

    # Layer 2: 动态验证
    VERIFIED_TEST = "verified_test"
    """
    测试执行验证
    特点：运行测试确认
    示例：测试确认函数实际被调用
    """

    # Layer 3: 运行时验证
    VERIFIED_RUNTIME = "verified_runtime"
    """
    运行时观察验证
    特点：生产/测试环境实际观察
    示例：运行时类型观察
    """

    # 待处理
    AMBIGUOUS = "ambiguous"
    """
    需人工确认
    特点：推断冲突或证据不足
    示例：多个模式匹配、命名模糊
    """

    @classmethod
    def from_string(cls, value: str) -> "ExtractionConfidence":
        """从字符串创建置信度"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.AMBIGUOUS