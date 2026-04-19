"""
契约基类模块

定义所有扩展点的抽象基类，遵循契约驱动设计原则：
- 输入输出明确
- 失败降级
- 不抛异常
- 可替换性
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from knowledgeforge.skeleton.result import ForgeResult


class ParserContract(ABC):
    """
    Parser扩展点契约

    输入：项目路径（Path对象）+ 解析模式
    输出：项目结构（Structure Dict）+ 置信度
    失败：返回 None

    行为约定：
        - 不能抛出异常，骨架不捕获
        - 失败时返回 None
        - 必须返回所有required字段
        - 必须标注置信度（tree-sitter解析应为EXTRACTED_STATIC）
        - 必须是确定性输出（同一输入同一输出）
    """

    @abstractmethod
    def parse(self, project_path: Path, mode: str = "full") -> Optional[Dict]:
        """
        解析项目结构

        Args:
            project_path: 项目根目录路径
            mode: 解析模式（"full" | "incremental"）

        Returns:
            Optional[Dict]: 成功返回Structure Dict，失败返回None

        注意：
            - 必须内部捕获所有异常
            - 必须标注置信度
            - tree-sitter解析置信度为EXTRACTED_STATIC
        """
        pass


class PatternExtractorContract(ABC):
    """
    PatternExtractor扩展点契约

    输入：项目结构（Structure对象）
    输出：设计模式列表（List[Pattern]）
    失败：返回空列表 []

    行为约定：
        - 不能抛出异常，骨架不捕获
        - 失败时返回空列表 []
        - 每个Dict必须符合Pattern JSON Schema
    """

    @abstractmethod
    def extract_patterns(self, structure: Dict) -> List[Dict]:
        """
        提取设计模式

        Args:
            structure: 项目结构信息（Parser输出）

        Returns:
            List[Dict]: 设计模式列表
            失败时返回 []
        """
        pass


class MentalExtractorContract(ABC):
    """
    MentalExtractor扩展点契约

    输入：项目结构（Structure对象）+ 可选文档内容
    输出：心智模型列表（List[MentalModel]）
    失败：返回空列表 []

    行为约定：
        - 不能抛出异常，骨架不捕获
        - 失败时返回空列表 []
        - docs可选，无文档时基于代码推断
    """

    @abstractmethod
    def extract_mental_models(
        self,
        structure: Dict,
        docs: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        提取心智模型

        Args:
            structure: 项目结构信息（Parser输出）
            docs: 可选文档内容列表

        Returns:
            List[Dict]: 心智模型列表
            失败时返回 []
        """
        pass


class TechExtractorContract(ABC):
    """
    TechExtractor扩展点契约（可选）

    输入：项目结构（Structure对象）
    输出：技术知识列表（List[TechKnowledge]）
    失败：返回空列表 []
    """

    @abstractmethod
    def extract_tech(self, structure: Dict) -> List[Dict]:
        """
        提取技术知识

        Args:
            structure: 项目结构信息（Parser输出）

        Returns:
            List[Dict]: 技术知识列表
            失败时返回 []
        """
        pass


class StorageContract(ABC):
    """
    Storage扩展点契约

    输入：知识数据包（Dict）
    输出：存储成功状态（bool）
    失败：返回 False

    行为约定：
        - 不能抛出异常，骨架不捕获
        - 失败时返回 False
    """

    @abstractmethod
    def save(self, knowledge: Dict) -> bool:
        """
        存储知识数据包

        Args:
            knowledge: 知识数据包

        Returns:
            bool: 存储成功返回 True，失败返回 False
        """
        pass


class VisualizerContract(ABC):
    """
    Visualizer扩展点契约

    输入：知识数据包（Dict）
    输出：可视化结果（文件路径或URL）
    失败：可以抛出异常（骨架会捕获）

    行为约定：
        - 可视化失败不影响主流程
        - 骨架会捕获异常并记录
    """

    @abstractmethod
    def render(self, knowledge: Dict) -> Optional[str]:
        """
        渲染可视化

        Args:
            knowledge: 知识数据包

        Returns:
            Optional[str]: 可视化结果路径或URL
        """
        pass


class IndexerContract(ABC):
    """
    Indexer扩展点契约

    输入：知识数据包（Dict）
    输出：索引更新状态（bool）
    失败：可以抛出异常（骨架会捕获）

    行为约定：
        - 索引失败不影响主流程
        - 骨架会捕获异常并记录
    """

    @abstractmethod
    def update(self, knowledge: Dict) -> bool:
        """
        更新索引

        Args:
            knowledge: 知识数据包

        Returns:
            bool: 更新成功返回 True
        """
        pass


class QueryContract(ABC):
    """
    Query扩展点契约

    输入：查询条件
    输出：查询结果列表
    """

    @abstractmethod
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        搜索知识

        Args:
            query: 搜索关键词
            filters: 可选过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        pass

    @abstractmethod
    def blast_radius(self, query: str) -> Dict:
        """
        影响范围分析

        Args:
            query: 目标符号（函数名、类名等）

        Returns:
            Dict: 影响范围分析结果
        """
        pass


class CacheManagerContract(ABC):
    """
    CacheManager扩展点契约

    输入：项目路径
    输出：变更文件列表、缓存结果
    """

    @abstractmethod
    def detect_changes(self, project_path: Path) -> List[Path]:
        """
        检测变更文件

        Args:
            project_path: 项目根目录路径

        Returns:
            List[Path]: 变更文件列表（空列表表示无变更）
        """
        pass

    @abstractmethod
    def save_result(self, project_path: Path, result: ForgeResult) -> bool:
        """
        缓存解析结果

        Args:
            project_path: 项目根目录路径
            result: 解析结果

        Returns:
            bool: 缓存成功返回 True
        """
        pass

    @abstractmethod
    def load_result(self, project_path: Path) -> Optional[ForgeResult]:
        """
        加载缓存结果

        Args:
            project_path: 项目根目录路径

        Returns:
            Optional[ForgeResult]: 缓存结果，无缓存返回 None
        """
        pass