"""
DefaultMentalExtractor - 默认心智模型提取器

基于文档和代码结构推断心智模型（Phase 0 基础版）。
"""

from typing import Dict, List, Optional

from knowledgeforge.skeleton.contracts import MentalExtractorContract


class DefaultMentalExtractor(MentalExtractorContract):
    """
    默认心智模型提取器

    Phase 0 基础版本：
    - 从文档提取心智模型（如果有README等）
    - 从代码结构推断设计心智模型
    - 无深度语义分析

    输出置信度：INFERRED_SEMANTIC
    """

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
        """
        mental_models = []

        try:
            if structure is None:
                return []

            # 如果有文档，优先从文档提取
            if docs:
                models_from_docs = self._extract_from_docs(docs, structure)
                mental_models.extend(models_from_docs)

            # 从代码结构推断心智模型
            models_from_structure = self._infer_from_structure(structure)
            mental_models.extend(models_from_structure)

            # 分配ID
            for i, model in enumerate(mental_models):
                model["id"] = f"M-{i+1:03d}"

        except Exception as e:
            print(f"[DefaultMentalExtractor] 处理异常: {e}")
            return []

        return mental_models

    def _extract_from_docs(self, docs: List[str], structure: Dict) -> List[Dict]:
        """从文档提取心智模型"""
        models = []

        for doc_content in docs:
            # 检测骨架设计心智模型
            if self._has_keywords(doc_content, ['骨架', 'skeleton', 'pipeline', '流水线']):
                models.append(self._create_skeleton_mental(doc_content, structure))

            # 检测契约心智模型
            if self._has_keywords(doc_content, ['契约', 'contract', '接口', 'interface', '抽象']):
                models.append(self._create_contract_mental(doc_content, structure))

            # 检测模块心智模型
            if self._has_keywords(doc_content, ['模块', 'module', '独立', 'independence']):
                models.append(self._create_module_mental(doc_content, structure))

        return models

    def _infer_from_structure(self, structure: Dict) -> List[Dict]:
        """从代码结构推断心智模型"""
        models = []

        # 推断骨架设计心智模型
        if structure.get("type") == "数据处理系统":
            models.append(self._create_default_skeleton_mental(structure))

        # 推断契约心智模型
        modules = structure.get("structure", {}).get("modules", [])
        if any('contract' in m.lower() or 'skeleton' in m.lower() for m in modules):
            models.append(self._create_default_contract_mental(structure))

        # 推断测试心智模型
        stats = structure.get("stats", {})
        if stats.get("code_files", 0) > 10:
            models.append(self._create_default_test_mental(structure))

        return models

    def _has_keywords(self, text: str, keywords: List[str]) -> bool:
        """检查文本是否包含关键词"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)

    def _create_skeleton_mental(self, doc: str, structure: Dict) -> Dict:
        """从文档创建骨架心智模型"""
        # 尝试提取核心洞察
        core_insight = self._extract_insight(doc, '骨架')
        if not core_insight:
            core_insight = "先设计骨架（流程+扩展点），再填充能力层"

        return {
            "id": "",
            "name": "骨架优先心智模型",
            "core_insight": core_insight,
            "why_valuable": "骨架稳定，能力层可迭代替换，降低系统复杂度",
            "author_cognition": "骨架只负责流程控制，不实现具体逻辑",
            "application_guidance": [
                "识别系统类型（数据处理vs交互）",
                "设计扩展点和契约",
                "提供默认实现",
                "逐步填充能力层"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_semantic",
            "evidence": {
                "confidence": "inferred_semantic",
                "reasoning": "从文档内容推断，文档包含骨架/skeleton关键词",
                "doc_hints": ["骨架", "skeleton"]
            }
        }

    def _create_contract_mental(self, doc: str, structure: Dict) -> Dict:
        """从文档创建契约心智模型"""
        core_insight = self._extract_insight(doc, '契约')
        if not core_insight:
            core_insight = "定义清晰契约，所有实现返回相同格式"

        return {
            "id": "",
            "name": "契约驱动心智模型",
            "core_insight": core_insight,
            "why_valuable": "契约明确接口，实现可替换，便于测试和扩展",
            "author_cognition": "骨架只依赖契约，不依赖具体实现",
            "application_guidance": [
                "定义输入输出格式",
                "定义失败处理约定",
                "定义行为约束",
                "提供多种实现"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_semantic",
            "evidence": {
                "confidence": "inferred_semantic",
                "reasoning": "从文档内容推断，文档包含契约/contract关键词",
                "doc_hints": ["契约", "contract"]
            }
        }

    def _create_module_mental(self, doc: str, structure: Dict) -> Dict:
        """从文档创建模块心智模型"""
        return {
            "id": "",
            "name": "模块独立心智模型",
            "core_insight": "模块职责单一，通过接口通信",
            "why_valuable": "降低耦合，便于并行开发和测试",
            "author_cognition": "每个模块只做一件事",
            "application_guidance": [
                "定义模块边界",
                "设计模块接口",
                "避免循环依赖",
                "保持模块独立性"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_semantic",
            "evidence": {
                "confidence": "inferred_semantic",
                "reasoning": "从文档内容推断，文档包含模块关键词",
                "doc_hints": ["模块", "module"]
            }
        }

    def _create_default_skeleton_mental(self, structure: Dict) -> Dict:
        """创建默认骨架心智模型"""
        return {
            "id": "",
            "name": "骨架优先心智模型",
            "core_insight": "先设计骨架（流程+扩展点），再填充能力层",
            "why_valuable": "骨架稳定，能力层可迭代替换",
            "author_cognition": "骨架只负责流程控制，不实现具体逻辑",
            "application_guidance": [
                "识别系统类型（数据处理vs交互）",
                "设计扩展点和契约",
                "提供默认实现"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "系统类型为数据处理系统，推断采用骨架设计",
                "structural_match": True
            }
        }

    def _create_default_contract_mental(self, structure: Dict) -> Dict:
        """创建默认契约心智模型"""
        return {
            "id": "",
            "name": "契约驱动心智模型",
            "core_insight": "定义清晰契约，所有实现返回相同格式",
            "why_valuable": "契约明确接口，实现可替换",
            "author_cognition": "骨架只依赖契约，不依赖具体实现",
            "application_guidance": [
                "定义输入输出格式",
                "定义失败处理约定"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "检测到contract/skeleton相关模块名",
                "structural_match": True
            }
        }

    def _create_default_test_mental(self, structure: Dict) -> Dict:
        """创建默认测试心智模型"""
        return {
            "id": "",
            "name": "测试先行心智模型",
            "core_insight": "测试是设计的一部分，不是事后补充",
            "why_valuable": "测试验证设计正确性，降低回归风险",
            "author_cognition": "每个模块都有对应的测试",
            "application_guidance": [
                "设计时考虑测试",
                "定义测试契约",
                "保持测试覆盖率"
            ],
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "项目规模较大（超过10个代码文件），推断需要测试",
                "structural_match": True
            }
        }

    def _extract_insight(self, doc: str, keyword: str) -> Optional[str]:
        """尝试从文档提取核心洞察"""
        lines = doc.split('\n')
        for line in lines:
            if keyword.lower() in line.lower():
                # 尝试提取描述性句子
                if len(line) > 20 and len(line) < 200:
                    return line.strip()
        return None