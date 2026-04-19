"""
LocalStorage - 本地文件存储

将知识数据包存储到本地文件系统。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

from knowledgeforge.skeleton.contracts import StorageContract


class LocalStorage(StorageContract):
    """
    本地文件存储

    将知识数据包存储为Markdown文件和JSON数据。
    """

    DEFAULT_OUTPUT_DIR = "knowledge_output"

    def __init__(self, output_dir: str = None):
        """
        初始化存储器

        Args:
            output_dir: 输出目录路径（默认为 knowledge_output）
        """
        self.output_dir = Path(output_dir or self.DEFAULT_OUTPUT_DIR)

    def save(self, knowledge: Dict) -> bool:
        """
        存储知识数据包

        Args:
            knowledge: 知识数据包

        Returns:
            bool: 存储成功返回 True，失败返回 False
        """
        try:
            # 创建输出目录
            self.output_dir.mkdir(parents=True, exist_ok=True)

            project_name = knowledge.get("case", {}).get("project_name", "unknown")

            # 1. 保存设计模式
            self._save_patterns(knowledge.get("patterns", []), project_name)

            # 2. 保存心智模型
            self._save_mental_models(knowledge.get("mental_models", []), project_name)

            # 3. 保存完整JSON
            self._save_json(knowledge, project_name)

            return True

        except Exception as e:
            print(f"[LocalStorage] 存储异常: {e}")
            return False

    def _save_patterns(self, patterns: list, project_name: str) -> None:
        """保存设计模式"""
        if not patterns:
            return

        patterns_dir = self.output_dir / "pattern-library"
        patterns_dir.mkdir(parents=True, exist_ok=True)

        for pattern in patterns:
            pattern_file = patterns_dir / f"{pattern.get('name', 'unknown')}.md"
            content = self._format_pattern_md(pattern, project_name)
            pattern_file.write_text(content, encoding='utf-8')

    def _save_mental_models(self, mental_models: list, project_name: str) -> None:
        """保存心智模型"""
        if not mental_models:
            return

        mental_dir = self.output_dir / "mental-model-library"
        mental_dir.mkdir(parents=True, exist_ok=True)

        for model in mental_models:
            model_file = mental_dir / f"{model.get('name', 'unknown')}.md"
            content = self._format_mental_md(model, project_name)
            model_file.write_text(content, encoding='utf-8')

    def _save_json(self, knowledge: Dict, project_name: str) -> None:
        """保存完整JSON"""
        json_dir = self.output_dir / "data"
        json_dir.mkdir(parents=True, exist_ok=True)

        json_file = json_dir / f"{project_name}-knowledge.json"
        json_file.write_text(json.dumps(knowledge, indent=2, ensure_ascii=False), encoding='utf-8')

    def _format_pattern_md(self, pattern: Dict, project_name: str) -> str:
        """格式化设计模式为Markdown"""
        return f"""# {pattern.get('name', '未知模式')}

> **来源项目:** {project_name}
> **置信度:** {pattern.get('confidence', 'unknown')}
> **模式ID:** {pattern.get('id', '')}

## 模式描述

{pattern.get('description', '')}

## 适用场景

{self._format_list(pattern.get('applicable_scenarios', []))}

## 不适用场景

{self._format_list(pattern.get('not_applicable_scenarios', []))}

## 代码模板

```
{pattern.get('code_template', '')}
```

## 证据记录

- **置信度:** {pattern.get('evidence', {}).get('confidence', 'unknown')}
- **推断理由:** {pattern.get('evidence', {}).get('reasoning', '')}
- **结构匹配:** {pattern.get('evidence', {}).get('structural_match', False)}

---
*生成时间: {datetime.now().isoformat()}*
"""

    def _format_mental_md(self, model: Dict, project_name: str) -> str:
        """格式化心智模型为Markdown"""
        return f"""# {model.get('name', '未知心智模型')}

> **来源项目:** {project_name}
> **置信度:** {model.get('confidence', 'unknown')}
> **模型ID:** {model.get('id', '')}

## 核心洞察

{model.get('core_insight', '')}

## 为什么有价值

{model.get('why_valuable', '')}

## 作者的认知

{model.get('author_cognition', '')}

## 应用指导

{self._format_list(model.get('application_guidance', []))}

## 证据记录

- **置信度:** {model.get('evidence', {}).get('confidence', 'unknown')}
- **推断理由:** {model.get('evidence', {}).get('reasoning', '')}

---
*生成时间: {datetime.now().isoformat()}*
"""

    def _format_list(self, items: list) -> str:
        """格式化列表"""
        if not items:
            return "无"
        return "\n".join(f"- {item}" for item in items)