# KnowledgeForge 版本发布记录

> **仓库地址:** https://github.com/zhengxingSong/KnowledgeForge

---

## v0.3.0 - Phase 2 完成

> **发布日期:** 2026-04-19
> **Git Tag:** v0.3.0
> **Commit:** Phase 2 验收通过

### 完成内容

#### Phase 2 新增功能
| 文件 | 功能 | 说明 |
|------|------|------|
| `mcp/server.py` | KnowledgeForgeMCPServer | MCP服务器实现 |
| `analysis/blast_radius.py` | BlastRadiusAnalyzer | 影响范围分析 |
| `verification/test_verify.py` | VerifyRunner | 测试验证运行器 |
| `tests/test_phase2.py` | Phase 2验收测试 | 20个测试 |

### 核心功能

**MCP服务器**
- MCP协议实现
- 工具定义: forge_project, query_patterns, blast_radius, get_evidence, list_projects
- Claude Desktop/Cursor集成配置生成

**BlastRadius分析**
- 模式影响范围分析
- 相关模块检测
- 相关模式相似度计算
- 风险等级评估

**Verify验证**
- 测试执行验证
- 置信度提升机制
- 测试成功率计算

### 测试结果

| 测试套件 | 测试数 | 结果 |
|----------|--------|------|
| Phase 0 | 24 | ✅ 全部通过 |
| Phase 1 | 26 | ✅ 全部通过 |
| Phase 2 | 20 | ✅ 全部通过 |
| **总计** | **70** | **✅ 全部通过** |

### CLI命令新增

| 命令 | 功能 |
|------|------|
| `blast-radius <pattern_id>` | 分析模式影响范围 |
| `verify <pattern_id>` | 运行测试验证模式 |
| `install --mcp` | 安装MCP服务器配置 |

### 下一步

Phase 3 规划：
- WebVisualizer实现
- 完整CLI命令
- 真实项目测试
- 产品化发布

---

## v0.2.0 - Phase 1 完成

> **发布日期:** 2026-04-19
> **Git Tag:** v0.2.0
> **Commit:** Phase 1 验收通过

### 完成内容

#### Phase 1 新增功能
| 文件 | 功能 | 说明 |
|------|------|------|
| `defaults/language_config.py` | LanguageConfig | 23+语言配置 |
| `defaults/tree_sitter_parser.py` | TreeSitterParser | tree-sitter AST解析 |
| `defaults/cache_manager.py` | CacheManager | SHA256缓存管理 |
| `tests/test_phase1.py` | Phase 1验收测试 | 26个测试 |

### 核心功能

**LanguageConfig (23+语言)**
- 支持Python、JavaScript、TypeScript、Go、Rust等23+语言
- 文件扩展名自动检测
- tree-sitter语言包映射

**TreeSitterParser (AST解析)**
- 零LLM消耗的AST解析
- 函数、类、import结构提取
- 支持incremental增量解析模式

**CacheManager (SHA256缓存)**
- 文件SHA256哈希计算
- 变更检测支持增量解析
- manifest.json缓存管理

**置信度系统集成**
- ExtractionConfidence 5级置信度
- ExtractionEvidence 证据记录
- 所有输出带confidence标注

### 测试结果

| 测试套件 | 测试数 | 结果 |
|----------|--------|------|
| Phase 0 | 24 | ✅ 全部通过 |
| Phase 1 | 26 | ✅ 全部通过 |
| **总计** | **50** | **✅ 全部通过** |

### 验收结果

| 测试项 | 结果 |
|--------|------|
| TC-101~110: LanguageConfig测试 | ✅ 通过 |
| TC-111~115: CacheManager测试 | ✅ 通过 |
| TC-116~121: 置信度系统测试 | ✅ 通过 |
| TC-122~126: TreeSitterParser测试 | ✅ 通过 |

### 下一步

Phase 2 规划：
- MCP服务器实现
- blast-radius影响范围分析
- verify测试验证命令
- EvidenceCollector证据收集

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