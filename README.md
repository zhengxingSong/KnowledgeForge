# KnowledgeForge

> **开源项目知识锻造系统** - 从开源项目中提取设计模式和心智模型

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.2.0-orange)](https://github.com/zhengxingSong/KnowledgeForge/releases)

## 🎯 项目能做什么？

KnowledgeForge 能够解析任意开源项目，自动提取并结构化输出：

| 提取内容 | 说明 | 示例 |
|---------|------|------|
| **设计模式** | 项目使用的架构模式 | 流水线骨架、契约驱动、模块独立、分层架构 |
| **心智模型** | 作者的设计思想 | 骨架优先、契约驱动、测试先行 |
| **项目结构** | 模块划分、入口点、配置文件 | 解析目录结构，识别系统类型 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/zhengxingSong/KnowledgeForge.git
cd KnowledgeForge

# 安装依赖
pip install -e .
```

### 使用 CLI

```bash
# 解析项目（使用完整命令）
knowledgeforge forge /path/to/your/project

# 或使用短命令
kf forge /path/to/your/project

# 搜索已提取的知识
kf query pipeline

# 列出已解析的项目
kf list
```

### Python API

```python
from knowledgeforge import KnowledgeForgePipeline
from pathlib import Path

# 创建管道
pipeline = KnowledgeForgePipeline()

# 解析项目
result = pipeline.forge(Path("/path/to/project"))

# 查看结果
print(f"项目: {result.project['name']}")
print(f"设计模式: {len(result.patterns)}")
print(f"心智模型: {len(result.mental_models)}")

for pattern in result.patterns:
    print(f"  [{pattern['id']}] {pattern['name']}")
```

## 📁 输出内容

解析完成后，会在 `knowledge_output/` 目录生成：

```
knowledge_output/
├── pattern-library/           # 设计模式 (Markdown)
│   ├── 流水线骨架模式.md
│   ├── 契约驱动模式.md
│   └── ...
├── mental-model-library/      # 心智模型 (Markdown)
│   ├── 骨架优先心智模型.md
│   ├── 契约驱动心智模型.md
│   └── ...
├── data/                      # JSON 数据
│   └── project-knowledge.json
└── index.json                 # 索引（用于搜索）
```

## 🏗️ 项目架构

```
knowledgeforge/
├── skeleton/              # 核心骨架（流程控制）
│   ├── pipeline.py        # 主流程: parse -> extract -> store -> index
│   ├── result.py          # ForgeResult 数据类
│   ├── confidence.py      # 5级置信度系统
│   ├── evidence.py        # 证据记录
│   └── contracts.py       # 契约基类（扩展点定义）
│
├── defaults/              # 默认实现
│   ├── parser.py          # 项目结构解析
│   ├── pattern_extractor.py  # 设计模式提取
│   ├── mental_extractor.py   # 心智模型提取
│   ├── storage.py         # 本地存储
│   └── indexer.py         # 索引管理
│
├── cli/                   # 命令行工具
│   └── main.py            # forge/query/list 命令
│
└── mcp/                   # MCP服务器（Phase 2）
```

## 📊 当前功能状态

| 功能 | Phase | 状态 | 说明 |
|------|-------|------|------|
| **项目结构解析** | Phase 0 | ✅ 已实现 | 扫描目录、识别语言、检测系统类型 |
| **设计模式提取** | Phase 0 | ✅ 已实现 | 规则匹配：流水线、契约、模块独立、分层 |
| **心智模型提取** | Phase 0 | ✅ 已实现 | 文档分析 + 结构推断 |
| **本地存储** | Phase 0 | ✅ 已实现 | Markdown + JSON 格式 |
| **CLI命令** | Phase 0 | ✅ 已实现 | forge/query/list |
| **LanguageConfig** | Phase 1 | ✅ 已实现 | 23+语言配置与检测 |
| **TreeSitterParser** | Phase 1 | ✅ 已实现 | AST解析、函数/类提取 |
| **CacheManager** | Phase 1 | ✅ 已实现 | SHA256缓存、增量解析 |
| **置信度系统** | Phase 1 | ✅ 已实现 | 5级置信度标注、证据链 |
| **tree-sitter解析** | Phase 1 | ✅ 已实现 | AST解析、零LLM消耗、23+语言 |
| **MCP集成** | Phase 2 | 🔜 待开发 | Claude Desktop/Cursor集成 |
| **影响范围分析** | Phase 2 | 🔜 待开发 | blast-radius 分析 |
| **Web可视化** | Phase 3 | 🔜 待开发 | 知识图谱、交互界面 |

## 🔍 设计模式示例

KnowledgeForge 当前可检测以下设计模式：

| 模式名称 | 检测依据 | 适用场景 |
|---------|---------|---------|
| **流水线骨架模式** | 目录含 pipeline/flow/process 或系统类型为数据处理 | ETL、批处理、数据转换 |
| **契约驱动模式** | 目录含 contract/interface/abstract | 插件系统、可替换实现 |
| **模块独立性模式** | 3+个独立模块 | 大型项目、团队协作 |
| **配置驱动模式** | 多个配置文件 | 多环境部署 |
| **分层架构模式** | api/service/data 等分层目录 | 企业应用 |

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 当前状态: 24 tests passed
```

## 📖 设计原则

1. **流程控制不变** - 骨架只负责 orchestration，不实现具体逻辑
2. **扩展点可拔插** - 通过构造函数注入，所有组件可替换
3. **失败降级** - Parser失败终止，其他失败继续运行
4. **结果标准化** - ForgeResult 统一输出格式
5. **置信度标注** - 所有提取结果附带置信度（Phase 1完整实现）

## 📄 文档

- [CLAUDE.md](CLAUDE.md) - 项目开发指南
- [RELEASES.md](RELEASES.md) - 版本发布记录
- 设计文档位于 `../products/knowledgeforge-design/`

## 📜 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**当前版本: v0.1.0 (Phase 0 完成)**