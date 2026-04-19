"""
JSONIndexer - JSON索引管理

维护知识索引，支持快速搜索。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from knowledgeforge.skeleton.contracts import IndexerContract


class JSONIndexer(IndexerContract):
    """
    JSON索引管理

    维护 index.json 文件，记录所有已解析的项目。
    """

    DEFAULT_INDEX_FILE = "knowledge_output/index.json"

    def __init__(self, index_file: str = None):
        """
        初始化索引器

        Args:
            index_file: 索引文件路径
        """
        self.index_file = Path(index_file or self.DEFAULT_INDEX_FILE)
        self._ensure_index_file()

    def update(self, knowledge: Dict) -> bool:
        """
        更新索引

        Args:
            knowledge: 知识数据包

        Returns:
            bool: 更新成功返回 True
        """
        try:
            index = self._load_index()

            project_name = knowledge.get("case", {}).get("project_name", "unknown")

            # 更新项目记录
            index["projects"][project_name] = {
                "name": project_name,
                "type": knowledge.get("case", {}).get("system_type", "未知"),
                "language": knowledge.get("case", {}).get("language", "未知"),
                "analysis_date": knowledge.get("case", {}).get("analysis_date", datetime.now().isoformat()),
                "patterns_count": len(knowledge.get("patterns", [])),
                "mental_models_count": len(knowledge.get("mental_models", [])),
                "forge_version": knowledge.get("metadata", {}).get("forge_version", "unknown")
            }

            # 更新模式索引
            for pattern in knowledge.get("patterns", []):
                pattern_id = pattern.get("id", "")
                index["patterns"][pattern_id] = {
                    "name": pattern.get("name", ""),
                    "source_project": project_name,
                    "confidence": pattern.get("confidence", "unknown")
                }

            # 更新心智模型索引
            for model in knowledge.get("mental_models", []):
                model_id = model.get("id", "")
                index["mental_models"][model_id] = {
                    "name": model.get("name", ""),
                    "source_project": project_name,
                    "confidence": model.get("confidence", "unknown")
                }

            # 更新统计
            index["stats"]["total_projects"] = len(index["projects"])
            index["stats"]["total_patterns"] = len(index["patterns"])
            index["stats"]["total_mental_models"] = len(index["mental_models"])
            index["stats"]["last_update"] = datetime.now().isoformat()

            self._save_index(index)

            return True

        except Exception as e:
            print(f"[JSONIndexer] 更新异常: {e}")
            return False

    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        搜索知识

        Args:
            query: 搜索关键词
            filters: 可选过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            index = self._load_index()
            results = []

            query_lower = query.lower()

            # 搜索模式
            for pattern_id, pattern in index.get("patterns", {}).items():
                if query_lower in pattern.get("name", "").lower():
                    results.append({
                        "type": "pattern",
                        "id": pattern_id,
                        "name": pattern.get("name", ""),
                        "source_project": pattern.get("source_project", "")
                    })

            # 搜索心智模型
            for model_id, model in index.get("mental_models", {}).items():
                if query_lower in model.get("name", "").lower():
                    results.append({
                        "type": "mental_model",
                        "id": model_id,
                        "name": model.get("name", ""),
                        "source_project": model.get("source_project", "")
                    })

            # 搜索项目
            for project_name, project in index.get("projects", {}).items():
                if query_lower in project_name.lower():
                    results.append({
                        "type": "project",
                        "name": project_name,
                        "patterns_count": project.get("patterns_count", 0),
                        "mental_models_count": project.get("mental_models_count", 0)
                    })

            # 应用过滤条件
            if filters:
                results = self._apply_filters(results, filters)

            return results

        except Exception as e:
            print(f"[JSONIndexer] 搜索异常: {e}")
            return []

    def blast_radius(self, query: str) -> Dict:
        """
        影响范围分析

        Phase 2 实现完整功能。

        Args:
            query: 目标符号（函数名、类名等）

        Returns:
            Dict: 影响范围分析结果
        """
        # Phase 0 基础实现：返回基本信息
        return {
            "target": query,
            "direct_callers": [],
            "transitive_callers": [],
            "confidence": "not_implemented",
            "note": "Phase 2 实现完整影响范围分析"
        }

    def _ensure_index_file(self) -> None:
        """确保索引文件存在"""
        if not self.index_file.exists():
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_index(self._create_empty_index())

    def _create_empty_index(self) -> Dict:
        """创建空索引结构"""
        return {
            "projects": {},
            "patterns": {},
            "mental_models": {},
            "stats": {
                "total_projects": 0,
                "total_patterns": 0,
                "total_mental_models": 0,
                "last_update": datetime.now().isoformat()
            },
            "version": "1.0"
        }

    def _load_index(self) -> Dict:
        """加载索引"""
        if not self.index_file.exists():
            return self._create_empty_index()

        try:
            content = self.index_file.read_text(encoding='utf-8')
            return json.loads(content)
        except Exception:
            return self._create_empty_index()

    def _save_index(self, index: Dict) -> None:
        """保存索引"""
        self.index_file.write_text(
            json.dumps(index, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """应用过滤条件"""
        filtered = []

        for result in results:
            match = True

            # 类型过滤
            if "type" in filters:
                if result.get("type") != filters["type"]:
                    match = False

            # 置信度过滤
            if "confidence" in filters:
                if result.get("confidence") != filters["confidence"]:
                    match = False

            # 项目过滤
            if "project" in filters:
                if result.get("source_project") != filters["project"]:
                    match = False

            if match:
                filtered.append(result)

        return filtered