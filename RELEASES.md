# KnowledgeForge 版本发布记录

> **仓库地址:** https://github.com/zhengxingSong/KnowledgeForge

---

## v0.1.0 - Phase 0 完成

> **发布日期:** 2026-04-19
> **Git Tag:** v0.1.0
> **Commit:** Phase 0 验收通过

### 完成内容

#### 骨架核心 (skeleton/)
| 文件 | 功能 | 行数 |
|------|------|------|
| `result.py` | ForgeResult 数据类 | 35 |
| `confidence.py` | 5级置信度枚举 (ExtractionConfidence) | 60 |
| `evidence.py` | 证据记录类 (ExtractionEvidence) | 50 |
| `contracts.py` | 7个契约基类 | 150 |
| `pipeline.py` | KnowledgeForgePipeline 核心骨架 | 180 |

#### 默认实现 (defaults/)
| 文件 | 功能 | 行数 |
|------|------|------|
| `parser.py` | DefaultParser (文件扫描) | 180 |
| `pattern_extractor.py` | DefaultPatternExtractor | 280 |
| `mental_extractor.py` | DefaultMentalExtractor | 200 |
| `storage.py` | LocalStorage (Markdown存储) | 120 |
| `indexer.py` | JSONIndexer | 150 |

#### CLI (cli/)
| 文件 | 功能 | 行数 |
|------|------|------|
| `main.py` | forge/query/list 命令 | 140 |

#### 测试
| 文件 | 功能 | 测试数 |
|------|------|--------|
| `test_phase0.py` | Phase 0 验收测试 | 24 (全部通过) |

### 验收结果

| 测试项 | 结果 |
|--------|------|
| TC-001: 骨架独立运行 | ✅ 通过 |
| TC-002: Parser失败降级 | ✅ 通过 |
| TC-003: Extractor失败降级 | ✅ 通过 |
| TC-005: 输出格式验证 | ✅ 通过 |

### 功能验证

解析自身项目结果：
- 发现设计模式: 1 (流水线骨架模式)
- 发现心智模型: 12 (骨架优先、契约驱动、模块独立等)

### 下一步

Phase 1 规划：
- tree-sitter AST 解析 (零LLM消耗)
- 置信度系统集成
- 增量解析 + SHA256缓存
- LanguageConfig (23+语言支持)

---

## 版本规划

| 版本 | Phase | 目标 | 状态 |
|------|-------|------|------|
| v0.1.0 | Phase 0 | 骨架跑起来 | ✅ 已发布 |
| v0.2.0 | Phase 1 | tree-sitter、置信度系统 | 待开发 |
| v0.3.0 | Phase 2 | MCP、影响范围分析 | 待开发 |
| v1.0.0 | Phase 3 | CLI完整、Web可视化、发布 | 待开发 |

---

**版本记录结束**