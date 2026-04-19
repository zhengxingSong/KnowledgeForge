"""
KnowledgeForge 骨架核心

主流程：解析 -> 提取 -> 存储 -> 可视化 -> 索引

骨架只负责流程控制，具体实现由能力层提供。
骨架不捕获异常，能力层返回特定值表示失败。

设计原则：
1. 流程控制不变：骨架只负责 orchestration
2. 扩展点可拔插：通过构造函数注入能力层
3. 失败降级：能力层失败时骨架记录并继续
4. 结果标准化：使用 ForgeResult 统一输出格式
5. 增量更新：支持增量解析，减少重复计算
6. 置信度标注：所有输出附带置信度信息
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from knowledgeforge.skeleton.result import ForgeResult
from knowledgeforge.skeleton.confidence import ExtractionConfidence


class KnowledgeForgePipeline:
    """
    KnowledgeForge 骨架核心

    主流程：解析 -> 提取 -> 存储 -> 可视化 -> 索引

    骨架只负责流程控制，具体实现由能力层提供。
    骨架不捕获异常，能力层返回特定值表示失败。
    """

    def __init__(
        self,
        parser: 'ParserContract' = None,
        pattern_extractor: 'PatternExtractorContract' = None,
        mental_extractor: 'MentalExtractorContract' = None,
        tech_extractor: 'TechExtractorContract' = None,
        storage: 'StorageContract' = None,
        visualizer: 'VisualizerContract' = None,
        indexer: 'IndexerContract' = None,
        cache_manager: 'CacheManagerContract' = None
    ):
        """
        初始化骨架，注入能力层实现。

        所有扩展点都有默认实现，骨架可独立运行。

        Args:
            parser: 项目解析器（必要扩展点）
            pattern_extractor: 设计模式提取器（必要扩展点）
            mental_extractor: 心智模型提取器（必要扩展点）
            tech_extractor: 技术知识提取器（可选扩展点）
            storage: 存储后端（必要扩展点）
            visualizer: 可视化组件（必要扩展点）
            indexer: 索引组件（必要扩展点）
            cache_manager: 缓存管理器（推荐扩展点）
        """
        # 延迟导入默认实现，避免循环依赖
        from knowledgeforge.defaults import (
            DefaultParser,
            DefaultPatternExtractor,
            DefaultMentalExtractor,
            LocalStorage,
            JSONIndexer
        )

        # 必要扩展点：有默认实现，骨架可独立运行
        self.parser = parser or DefaultParser()
        self.pattern_extractor = pattern_extractor or DefaultPatternExtractor()
        self.mental_extractor = mental_extractor or DefaultMentalExtractor()
        self.tech_extractor = tech_extractor  # 可选扩展点，无默认实现
        self.storage = storage or LocalStorage()
        self.visualizer = visualizer  # 可选扩展点，Phase 3 实现
        self.indexer = indexer or JSONIndexer()
        self.cache_manager = cache_manager  # 可选扩展点，Phase 1 实现

        # 骨架状态
        self._last_forge_result: Optional[ForgeResult] = None
        self._forge_history: List[ForgeResult] = []

    def forge(self, project_path: Path, mode: str = "full") -> ForgeResult:
        """
        解析开源项目，锻造知识。

        流程：parse -> extract -> store -> visualize -> index

        Args:
            project_path: 项目根目录路径
            mode: 解析模式
                - "full": 全量解析（忽略缓存）
                - "incremental": 增量解析（仅解析变更文件）
                - "verify": 验证模式（运行测试验证推断）

        Returns:
            ForgeResult: 处理结果
        """
        result = ForgeResult()
        result.parse_metadata["mode"] = mode

        # ====== Phase 0: 增量检测 ======
        if mode == "incremental" and self.cache_manager:
            changed_files = self.cache_manager.detect_changes(project_path)
            if not changed_files:
                # 无变更，直接返回缓存结果
                cached_result = self.cache_manager.load_result(project_path)
                if cached_result:
                    cached_result.parse_metadata["cache_hit"] = True
                    return cached_result
            result.parse_metadata["changed_files"] = len(changed_files) if changed_files else 0

        # ====== Phase 1: 解析项目结构 ======
        structure = self.parser.parse(project_path, mode)
        if structure is None:
            result.errors.append({
                "phase": "parse",
                "error": "Parser返回None，解析失败",
                "fallback": "骨架终止，返回失败结果"
            })
            return result  # Parser失败是致命错误，无法继续

        result.project = structure
        result.parse_metadata["parse_time_ms"] = structure.get("_parse_time_ms", 0)
        result.parse_metadata["confidence"] = structure.get("_confidence", "extracted_static")

        # ====== Phase 2: 提取设计模式 ======
        patterns = self.pattern_extractor.extract_patterns(structure)
        if patterns is None or len(patterns) == 0:
            result.errors.append({
                "phase": "extract_patterns",
                "error": "PatternExtractor返回空列表",
                "fallback": "骨架继续，patterns为空"
            })
            patterns = []
        # 过滤置信度
        result.parse_metadata["pattern_confidence_distribution"] = self._count_confidence(patterns)
        result.patterns = patterns

        # ====== Phase 3: 提取心智模型 ======
        docs = self._load_docs(structure, project_path)
        mental_models = self.mental_extractor.extract_mental_models(structure, docs)
        if mental_models is None:
            mental_models = []
        result.parse_metadata["mental_confidence_distribution"] = self._count_confidence(mental_models)
        result.mental_models = mental_models

        # ====== Phase 4: 提取技术知识（可选） ======
        if self.tech_extractor is not None:
            tech_knowledge = self.tech_extractor.extract_tech(structure)
            if tech_knowledge is None:
                tech_knowledge = []
            result.tech_knowledge = tech_knowledge

        # ====== Phase 5: 动态验证（可选） ======
        if mode == "verify":
            verified_result = self._verify_with_tests(project_path, result)
            result = verified_result

        # ====== Phase 6: 构建知识数据包 ======
        knowledge = self._build_knowledge_package(structure, patterns, mental_models, result.tech_knowledge)

        # ====== Phase 7: 存储知识 ======
        storage_success = self.storage.save(knowledge)
        if not storage_success:
            result.errors.append({
                "phase": "store",
                "error": "Storage返回False，存储失败",
                "fallback": "骨架继续，但知识未持久化"
            })

        # ====== Phase 8: 可视化 ======
        if self.visualizer is not None:
            try:
                self.visualizer.render(knowledge)
            except Exception as e:
                result.errors.append({
                    "phase": "visualize",
                    "error": f"Visualizer失败: {str(e)}",
                    "fallback": "骨架继续，可视化降级"
                })

        # ====== Phase 9: 更新索引 ======
        try:
            self.indexer.update(knowledge)
        except Exception as e:
            result.errors.append({
                "phase": "index",
                "error": f"Indexer失败: {str(e)}",
                "fallback": "骨架继续，索引未更新"
            })

        # ====== Phase 10: 缓存结果 ======
        if self.cache_manager:
            self.cache_manager.save_result(project_path, result)

        # ====== 完成 ======
        # Parser失败是致命错误，其他失败不影响 success
        result.success = len([e for e in result.errors if e.get("phase") == "parse"]) == 0
        self._last_forge_result = result
        self._forge_history.append(result)

        return result

    def _count_confidence(self, items: List[Dict]) -> Dict:
        """统计置信度分布"""
        counts = {}
        for item in items:
            conf = item.get("confidence", "unknown")
            counts[conf] = counts.get(conf, 0) + 1
        return counts

    def _verify_with_tests(self, project_path: Path, result: ForgeResult) -> ForgeResult:
        """运行测试验证推断（可选动态验证）"""
        # TODO: Phase 2 实现测试执行追踪
        # 参考 graphify 的动态验证机制
        return result

    def _build_knowledge_package(
        self,
        structure: Dict,
        patterns: List[Dict],
        mental_models: List[Dict],
        tech_knowledge: List[Dict]
    ) -> Dict:
        """
        构建标准化的知识数据包。
        """
        return {
            "patterns": patterns,
            "mental_models": mental_models,
            "tech_knowledge": tech_knowledge or [],
            "case": {
                "project_name": structure.get("name", "unknown"),
                "analysis_date": datetime.now().isoformat(),
                "system_type": structure.get("type", "未知"),
                "language": structure.get("language", "未知"),
                "stats": structure.get("stats", {}),
                "structure": structure.get("structure", {})
            },
            "metadata": {
                "forge_version": "2.0",
                "parse_mode": structure.get("_parse_mode", "full"),
                "confidence_system": "v1.0"
            }
        }

    def _load_docs(self, structure: Dict, project_path: Path) -> Optional[List[str]]:
        """加载文档内容"""
        doc_files = structure.get("doc_files", [])
        if not doc_files:
            return None

        docs = []
        for doc_path in doc_files:
            try:
                # 处理相对路径
                if not Path(doc_path).is_absolute():
                    full_path = project_path / doc_path
                else:
                    full_path = Path(doc_path)

                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8')
                    docs.append(content)
            except Exception:
                continue

        return docs if docs else None

    def get_last_result(self) -> Optional[ForgeResult]:
        """获取最后一次处理结果"""
        return self._last_forge_result

    def get_history(self) -> List[ForgeResult]:
        """获取处理历史"""
        return self._forge_history