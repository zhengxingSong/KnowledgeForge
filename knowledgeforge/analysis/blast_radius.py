"""
BlastRadiusAnalyzer - 影响范围分析模块

分析设计模式的影响范围：
- 相关模块
- 依赖模式
- 调用链
- 修改风险
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

from knowledgeforge.defaults.indexer import JSONIndexer
from knowledgeforge.defaults.storage import LocalStorage


class BlastRadiusAnalyzer:
    """
    影响范围分析器

    分析设计模式的影响范围：
    - 相关模块
    - 依赖模式
    - 调用链
    - 修改风险
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化分析器

        Args:
            output_dir: 知识输出目录
        """
        self.indexer = JSONIndexer()
        output_dir_str = str(output_dir) if output_dir else None
        self.storage = LocalStorage(output_dir=output_dir_str)

    def analyze(
        self,
        pattern_id: str,
        depth: int = 3,
        project_filter: Optional[str] = None
    ) -> Dict:
        """
        分析模式影响范围

        Args:
            pattern_id: 模式ID
            depth: 分析深度 (1-5)
            project_filter: 项目过滤

        Returns:
            Dict: 影响范围分析结果
        """
        # 1. 查找模式
        pattern = self._find_pattern(pattern_id, project_filter)
        if not pattern:
            return {
                "error": f"Pattern not found: {pattern_id}",
                "pattern_id": pattern_id
            }

        # 2. 分析源文件
        source_file = pattern.get("source_file", "")
        project_name = pattern.get("_project", project_filter)

        # 3. 分析相关模块
        affected_modules = self._analyze_modules(pattern, depth)

        # 4. 分析相关模式
        related_patterns = self._find_related_patterns(pattern, project_name)

        # 5. 分析调用链（如果有AST数据）
        call_chain = self._analyze_call_chain(pattern, depth)

        # 6. 计算风险等级
        risk_level = self._calculate_risk(pattern, affected_modules, related_patterns)

        # 7. 构建结果
        result = {
            "pattern_id": pattern_id,
            "pattern_name": pattern.get("name"),
            "source_file": source_file,
            "confidence": pattern.get("confidence"),
            "analysis_depth": depth,

            # 影响范围
            "affected_modules": affected_modules,
            "related_patterns": related_patterns,
            "call_chain": call_chain,

            # 风险评估
            "risk_level": risk_level,
            "modification_recommendation": self._get_recommendation(risk_level),

            # 证据
            "evidence": pattern.get("evidence", {})
        }

        return result

    def analyze_by_name(
        self,
        pattern_name: str,
        project_name: Optional[str] = None
    ) -> Dict:
        """
        通过模式名分析（模糊匹配）

        Args:
            pattern_name: 模式名称（可部分匹配）
            project_name: 项目名过滤

        Returns:
            Dict: 分析结果
        """
        # 查找匹配的模式
        pattern = self._find_pattern_by_name(pattern_name, project_name)

        if not pattern:
            return {
                "error": f"Pattern not found matching: {pattern_name}",
                "search_term": pattern_name
            }

        return self.analyze(pattern.get("id"), project_filter=project_name)

    def _find_pattern(self, pattern_id: str, project_filter: Optional[str] = None) -> Optional[Dict]:
        """查找模式"""
        index_data = self.indexer.load_index()

        if not index_data:
            return None

        # 直接从 patterns dict 查找
        patterns = index_data.get("patterns", {})
        if pattern_id in patterns:
            pattern = patterns[pattern_id]

            # 检查项目过滤
            if project_filter:
                source_project = pattern.get("source_project", "")
                if source_project != project_filter:
                    return None

            pattern["_project"] = pattern.get("source_project")
            return pattern

        return None

    def _find_pattern_by_name(self, pattern_name: str, project_name: Optional[str] = None) -> Optional[Dict]:
        """通过名称查找模式"""
        index_data = self.indexer.load_index()

        if not index_data:
            return None

        name_lower = pattern_name.lower()

        for project_entry in index_data.get("projects", []):
            if project_name and project_entry.get("name") != project_name:
                continue

            for pattern in project_entry.get("patterns", []):
                pattern_name_lower = pattern.get("name", "").lower()
                if name_lower in pattern_name_lower or pattern_name_lower in name_lower:
                    pattern["_project"] = project_entry.get("name")
                    return pattern

        return None

    def _analyze_modules(self, pattern: Dict, depth: int) -> List[Dict]:
        """分析相关模块"""
        modules = []

        # 从模式结构中提取模块
        evidence = pattern.get("evidence", {})
        naming_hints = evidence.get("naming_hints", [])

        # 添加命名提示作为相关模块
        for hint in naming_hints:
            modules.append({
                "name": hint,
                "relation": "naming_hint",
                "confidence": evidence.get("confidence")
            })

        # 从模式应用场景推断相关模块
        scenarios = pattern.get("applicable_scenarios", [])
        for scenario in scenarios:
            if "数据处理" in scenario or "ETL" in scenario:
                modules.append({
                    "name": "pipeline",
                    "relation": "scenario_match",
                    "confidence": "inferred"
                })
            if "API" in scenario or "交互" in scenario:
                modules.append({
                    "name": "api",
                    "relation": "scenario_match",
                    "confidence": "inferred"
                })

        return modules[:depth * 2]  # 根据深度限制结果

    def _find_related_patterns(self, pattern: Dict, project_name: Optional[str] = None) -> List[Dict]:
        """查找相关模式"""
        related = []

        index_data = self.indexer.load_index()
        if not index_data:
            return related

        # 当前模式的特征
        current_name = pattern.get("name", "").lower()
        current_scenarios = set(pattern.get("applicable_scenarios", []))

        # 搜索所有模式
        patterns = index_data.get("patterns", {})
        for other_id, other_pattern in patterns.items():
            if other_id == pattern.get("id"):
                continue

            # 项目过滤
            if project_name and other_pattern.get("source_project") != project_name:
                continue

            other_name = other_pattern.get("name", "").lower()
            other_scenarios = set(other_pattern.get("applicable_scenarios", []))

            # 计算相似度
            similarity = self._calculate_similarity(
                current_name, current_scenarios,
                other_name, other_scenarios
            )

            if similarity > 0.3:  # 相似度阈值
                related.append({
                    "pattern_id": other_id,
                    "pattern_name": other_pattern.get("name"),
                    "similarity": similarity,
                    "confidence": other_pattern.get("confidence")
                })

        # 按相似度排序
        related.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        return related[:5]  # 返回前5个

    def _calculate_similarity(
        self,
        name1: str,
        scenarios1: Set[str],
        name2: str,
        scenarios2: Set[str]
    ) -> float:
        """计算模式相似度"""
        # 名称相似度
        name_sim = 0.0
        if name1 and name2:
            # 检查关键词重叠
            keywords1 = set(name1.replace("模式", "").split())
            keywords2 = set(name2.replace("模式", "").split())
            if keywords1 & keywords2:
                name_sim = len(keywords1 & keywords2) / max(len(keywords1), len(keywords2), 1)

        # 场景相似度
        scenario_sim = 0.0
        if scenarios1 and scenarios2:
            overlap = scenarios1 & scenarios2
            scenario_sim = len(overlap) / max(len(scenarios1), len(scenarios2), 1)

        # 综合相似度
        return (name_sim * 0.4 + scenario_sim * 0.6)

    def _analyze_call_chain(self, pattern: Dict, depth: int) -> List[Dict]:
        """分析调用链"""
        # Phase 2 基础实现：基于模式代码模板推断调用链
        call_chain = []

        code_template = pattern.get("code_template", "")
        if not code_template:
            return call_chain

        # 从代码模板提取函数/类名
        import re

        # 提取函数定义
        functions = re.findall(r'def\s+(\w+)\s*\(', code_template)
        for func in functions:
            call_chain.append({
                "type": "function",
                "name": func,
                "relation": "defined_in_pattern",
                "depth": 1
            })

        # 提取类定义
        classes = re.findall(r'class\s+(\w+)', code_template)
        for cls in classes:
            call_chain.append({
                "type": "class",
                "name": cls,
                "relation": "defined_in_pattern",
                "depth": 1
            })

        return call_chain[:depth * 3]

    def _calculate_risk(self, pattern: Dict, modules: List, related: List) -> str:
        """计算风险等级"""
        # 基于以下因素计算风险：
        # 1. 置信度（低置信度 = 高风险）
        # 2. 影响模块数量
        # 3. 相关模式数量

        confidence = pattern.get("confidence", "ambiguous")

        # 置信度风险权重
        confidence_risk = {
            "extracted_static": 1,
            "inferred_pattern": 2,
            "inferred_semantic": 3,
            "verified_test": 1,
            "verified_runtime": 1,
            "ambiguous": 4
        }

        risk_score = confidence_risk.get(confidence, 3)

        # 模块数量风险
        risk_score += len(modules) * 0.5

        # 相关模式数量风险
        risk_score += len(related) * 0.3

        # 计算风险等级
        if risk_score <= 2:
            return "low"
        elif risk_score <= 4:
            return "medium"
        else:
            return "high"

    def _get_recommendation(self, risk_level: str) -> str:
        """获取修改建议"""
        recommendations = {
            "low": "可以直接修改，影响范围有限。",
            "medium": "修改前需检查相关模块，建议先运行测试验证。",
            "high": "修改风险较高，建议先提升置信度（运行测试验证），再进行修改。"
        }
        return recommendations.get(risk_level, "建议先评估影响范围。")


# 全局分析器实例
_global_analyzer: Optional[BlastRadiusAnalyzer] = None


def get_blast_radius_analyzer() -> BlastRadiusAnalyzer:
    """获取全局分析器实例"""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = BlastRadiusAnalyzer()
    return _global_analyzer