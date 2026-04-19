"""
WebVisualizer - Web可视化模块

生成静态HTML文件，展示设计模式和心智模型。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from knowledgeforge.skeleton.contracts import VisualizerContract
from knowledgeforge.skeleton.result import ForgeResult
from knowledgeforge.defaults.indexer import JSONIndexer


class WebVisualizer(VisualizerContract):
    """
    Web可视化生成器

    生成静态HTML文件，包含：
    - Pattern卡片
    - Mental Model卡片
    - 关系图
    - CSS/JS资源
    """

    DEFAULT_OUTPUT_DIR = "knowledge_output/visuals"

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化可视化器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir or self.DEFAULT_OUTPUT_DIR)

    def render(self, knowledge: Dict) -> Optional[str]:
        """
        渲染可视化

        Args:
            knowledge: 知识数据包

        Returns:
            Optional[str]: 生成的HTML文件路径
        """
        try:
            # 确保1输出目录存在
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # 生成HTML文件
            html_path = self.output_dir / "index.html"

            html_content = self.generate_html_content(knowledge)

            html_path.write_text(html_content, encoding='utf-8')

            return str(html_path)

        except Exception as e:
            print(f"[WebVisualizer] 渲染失败: {e}")
            return None

    def generate_html(self, result: ForgeResult) -> Path:
        """
        从ForgeResult生成HTML

        Args:
            result: 解析结果

        Returns:
            Path: 生成的HTML文件路径
        """
        knowledge = result.to_dict()
        html_path = self.render(knowledge)

        if html_path:
            return Path(html_path)
        else:
            return self.output_dir / "index.html"

    def generate_html_content(self, knowledge: Dict) -> str:
        """
        生成HTML内容

        Args:
            knowledge: 知识数据包

        Returns:
            str: HTML内容
        """
        # 提取数据
        project = knowledge.get("project", {})
        patterns = knowledge.get("patterns", [])
        mental_models = knowledge.get("mental_models", [])

        # 生成HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KnowledgeForge - {project.get('name', 'Unknown Project')}</title>
    <style>
{self.generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>KnowledgeForge</h1>
            <p class="subtitle">设计模式与心智模型可视化</p>
        </header>

        <section class="project-info">
            <h2>项目信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">项目名</span>
                    <span class="value">{project.get('name', 'Unknown')}</span>
                </div>
                <div class="info-item">
                    <span class="label">类型</span>
                    <span class="value">{project.get('type', 'Unknown')}</span>
                </div>
                <div class="info-item">
                    <span class="label">语言</span>
                    <span class="value">{project.get('language', 'Unknown')}</span>
                </div>
                <div class="info-item">
                    <span class="label">设计模式</span>
                    <span class="value">{len(patterns)}</span>
                </div>
                <div class="info-item">
                    <span class="label">心智模型</span>
                    <span class="value">{len(mental_models)}</span>
                </div>
            </div>
        </section>

        <section class="patterns-section">
            <h2>设计模式 ({len(patterns)})</h2>
            <div class="cards-grid">
{self._generate_pattern_cards(patterns)}
            </div>
        </section>

        <section class="mental-section">
            <h2>心智模型 ({len(mental_models)})</h2>
            <div class="cards-grid">
{self._generate_mental_cards(mental_models)}
            </div>
        </section>

        <footer>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>KnowledgeForge v0.3.0</p>
        </footer>
    </div>

    <script>
{self.generate_js()}
    </script>
</body>
</html>"""

        return html

    def generate_css(self) -> str:
        """生成CSS样式"""
        return """
        :root {
            --primary-color: #2563eb;
            --secondary-color: #3b82f6;
            --accent-color: #10b981;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 12px;
            margin-bottom: 40px;
        }

        header h1 {
            margin: 0;
            font-size: 2.5em;
        }

        header .subtitle {
            margin-top: 10px;
            opacity: 0.9;
        }

        .project-info {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }

        .project-info h2 {
            margin-top: 0;
            color: var(--primary-color);
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: var(--bg-color);
            border-radius: 8px;
        }

        .info-item .label {
            color: #64748b;
        }

        .info-item .value {
            font-weight: 600;
        }

        .patterns-section, .mental-section {
            margin-bottom: 40px;
        }

        .patterns-section h2, .mental-section h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .card-title {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--text-color);
        }

        .card-id {
            background: var(--primary-color);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8em;
        }

        .card-description {
            color: #64748b;
            margin-bottom: 15px;
            line-height: 1.6;
        }

        .confidence-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .confidence-extracted_static {
            background: #dcfce7;
            color: #166534;
        }

        .confidence-inferred_pattern {
            background: #fef3c7;
            color: #92400e;
        }

        .confidence-inferred_semantic {
            background: #fef9c3;
            color: #854d0e;
        }

        .confidence-verified_test {
            background: #d1fae5;
            color: #065f46;
        }

        .confidence-ambiguous {
            background: #fee2e2;
            color: #991b1b;
        }

        .scenarios-list {
            margin-top: 15px;
        }

        .scenarios-list h4 {
            color: #64748b;
            font-size: 0.9em;
            margin-bottom: 8px;
        }

        .scenarios-list ul {
            list-style: none;
            padding: 0;
        }

        .scenarios-list li {
            padding: 6px 0;
            color: #475569;
            border-bottom: 1px solid var(--border-color);
        }

        .scenarios-list li:last-child {
            border-bottom: none;
        }

        footer {
            text-align: center;
            padding: 40px;
            color: #64748b;
        }

        @media (max-width: 768px) {
            .cards-grid {
                grid-template-columns: 1fr;
            }

            .info-grid {
                grid-template-columns: 1fr;
            }
        }
"""

    def generate_js(self) -> str:
        """生成JavaScript"""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            // 卡片点击事件
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    // 展开/收起详情
                    this.classList.toggle('expanded');
                });
            });

            // 搜索功能
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const query = this.value.toLowerCase();
                    cards.forEach(card => {
                        const title = card.querySelector('.card-title').textContent.toLowerCase();
                        if (title.includes(query)) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    });
                });
            }
        });
"""

    def _generate_pattern_cards(self, patterns: List[Dict]) -> str:
        """生成Pattern卡片HTML"""
        cards_html = []

        for pattern in patterns:
            confidence = pattern.get("confidence", "ambiguous")
            confidence_class = f"confidence-{confidence}"

            # 场景列表
            applicable = pattern.get("applicable_scenarios", [])
            scenarios_html = ""
            if applicable:
                scenarios_html = f"""
                <div class="scenarios-list">
                    <h4>适用场景</h4>
                    <ul>
                        {"".join(f"<li>{s}</li>" for s in applicable[:5])}
                    </ul>
                </div>
"""

            card = f"""
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">{pattern.get('name', 'Unknown')}</span>
                        <span class="card-id">{pattern.get('id', '')}</span>
                    </div>
                    <p class="card-description">{pattern.get('description', '')[:150]}...</p>
                    <span class="confidence-badge {confidence_class}">{confidence}</span>
                    {scenarios_html}
                </div>
"""
            cards_html.append(card)

        return "\n".join(cards_html)

    def _generate_mental_cards(self, mental_models: List[Dict]) -> str:
        """生成Mental Model卡片HTML"""
        cards_html = []

        for model in mental_models:
            confidence = model.get("confidence", "ambiguous")
            confidence_class = f"confidence-{confidence}"

            # 应用指导
            guidance = model.get("application_guidance", [])
            guidance_html = ""
            if guidance:
                guidance_html = f"""
                <div class="scenarios-list">
                    <h4>应用指导</h4>
                    <ul>
                        {"".join(f"<li>{g}</li>" for g in guidance[:5])}
                    </ul>
                </div>
"""

            card = f"""
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">{model.get('name', 'Unknown')}</span>
                        <span class="card-id">{model.get('id', '')}</span>
                    </div>
                    <p class="card-description">{model.get('core_insight', '')[:150]}...</p>
                    <span class="confidence-badge {confidence_class}">{confidence}</span>
                    {guidance_html}
                </div>
"""
            cards_html.append(card)

        return "\n".join(cards_html)

    def generate_visualization_from_index(self) -> Path:
        """
        从index.json生成可视化

        Returns:
            Path: 生成的HTML文件路径
        """
        indexer = JSONIndexer()
        index_data = indexer.load_index()

        # 构建知识数据包
        patterns = []
        for pattern_id, pattern_data in index_data.get("patterns", {}).items():
            patterns.append({
                "id": pattern_id,
                "name": pattern_data.get("name"),
                "confidence": pattern_data.get("confidence"),
                "source_project": pattern_data.get("source_project")
            })

        mental_models = []
        for model_id, model_data in index_data.get("mental_models", {}).items():
            mental_models.append({
                "id": model_id,
                "name": model_data.get("name"),
                "confidence": model_data.get("confidence"),
                "source_project": model_data.get("source_project")
            })

        knowledge = {
            "project": {
                "name": "Knowledge Base",
                "type": "知识库",
                "language": "多语言"
            },
            "patterns": patterns,
            "mental_models": mental_models
        }

        return self.generate_html(ForgeResult(
            project=knowledge.get("project"),
            patterns=patterns,
            mental_models=mental_models,
            success=True
        ))


# 全局可视化器实例
_global_visualizer: Optional[WebVisualizer] = None


def get_web_visualizer() -> WebVisualizer:
    """获取全局可视化器实例"""
    global _global_visualizer
    if _global_visualizer is None:
        _global_visualizer = WebVisualizer()
    return _global_visualizer