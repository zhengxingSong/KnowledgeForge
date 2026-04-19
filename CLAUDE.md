# KnowledgeForge

开源项目知识锻造系统 - 从开源项目中提取设计模式和心智模型。

## 项目概述

KnowledgeForge 是一个 Python 工具，用于解析开源项目并提取：
- **设计模式**：如流水线骨架、契约驱动、模块独立等
- **心智模型**：如骨架优先、契约驱动等设计思想

## 架构设计

### 核心骨架 (skeleton/)
```
skeleton/
├── pipeline.py      # 主流程骨架 (parse -> extract -> store -> visualize -> index)
├── result.py        # ForgeResult 数据类
├── confidence.py    # 5级置信度枚举 (EXTRACTED_STATIC -> AMBIGUOUS)
├── evidence.py      # 证据记录类
└── contracts.py     # 契约基类 (ParserContract, ExtractorContract等)
```

### 默认实现 (defaults/)
```
defaults/
├── parser.py              # DefaultParser (Phase 0: 文件扫描)
├── pattern_extractor.py   # DefaultPatternExtractor (规则匹配)
├── mental_extractor.py    # DefaultMentalExtractor (文档+结构推断)
├── storage.py             # LocalStorage (Markdown + JSON)
└── indexer.py             # JSONIndexer (index.json)
```

### CLI (cli/)
```
cli/main.py
├── forge <path>   # 解析项目
├── query <term>   # 搜索知识
└── list           # 列出已解析项目
```

## 使用方式

```bash
# 安装
pip install knowledgeforge

# 解析项目
knowledgeforge forge /path/to/project

# 或使用别名
kf forge /path/to/project

# 搜索
kf query pipeline

# 列出
kf list
```

## Python API

```python
from knowledgeforge import KnowledgeForgePipeline

pipeline = KnowledgeForgePipeline()
result = pipeline.forge("/path/to/project")

print(f"Patterns: {len(result.patterns)}")
print(f"Mental Models: {len(result.mental_models)}")
```

## 开发阶段

| Phase | 目标 | 状态 |
|-------|-----|------|
| Phase 0 | 骨架跑起来（基础解析、存储、CLI） | ✅ 完成 |
| Phase 1 | tree-sitter解析、置信度系统、增量更新 | 待开始 |
| Phase 2 | MCP集成、影响范围分析、动态验证 | 待开始 |
| Phase 3 | 完整CLI、Web可视化、产品化 | 待开始 |

## 关键设计原则

1. **流程控制不变**：骨架只负责 orchestration
2. **扩展点可拔插**：通过构造函数注入能力层
3. **失败降级**：Parser失败终止，其他失败继续
4. **结果标准化**：ForgeResult 统一输出格式
5. **置信度标注**：所有输出附带置信度信息

## 测试

```bash
pytest tests/ -v
```

## 输出目录结构

```
knowledge_output/
├── pattern-library/      # 设计模式 Markdown
├── mental-model-library/ # 心智模型 Markdown
├── data/                 # JSON 数据
└── index.json            # 索引文件
```

## 相关文档

设计文档位于：`../products/knowledgeforge-design/`