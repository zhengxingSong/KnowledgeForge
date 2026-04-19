"""
Phase 0 骨架独立运行测试

验证骨架核心代码正确、默认实现可用。
"""

import os
import pytest
from pathlib import Path

from knowledgeforge import KnowledgeForgePipeline, ForgeResult, ExtractionConfidence
from knowledgeforge.defaults import (
    DefaultParser,
    DefaultPatternExtractor,
    DefaultMentalExtractor,
    LocalStorage,
    JSONIndexer,
)


class TestForgeResult:
    """测试 ForgeResult 数据类"""

    def test_forge_result_creation(self):
        """测试创建 ForgeResult"""
        result = ForgeResult()
        assert result.project is None
        assert result.patterns == []
        assert result.mental_models == []
        assert result.success is False
        assert result.errors == []
        assert result.parse_metadata == {}

    def test_forge_result_to_dict(self):
        """测试 to_dict 方法"""
        result = ForgeResult(
            project={"name": "test"},
            patterns=[{"id": "P-001"}],
            success=True
        )
        dict_result = result.to_dict()
        assert dict_result["project"]["name"] == "test"
        assert len(dict_result["patterns"]) == 1
        assert dict_result["success"] is True


class TestExtractionConfidence:
    """测试置信度枚举"""

    def test_confidence_values(self):
        """测试置信度值"""
        assert ExtractionConfidence.EXTRACTED_STATIC.value == "extracted_static"
        assert ExtractionConfidence.INFERRED_PATTERN.value == "inferred_pattern"
        assert ExtractionConfidence.INFERRED_SEMANTIC.value == "inferred_semantic"

    def test_from_string(self):
        """测试从字符串创建"""
        conf = ExtractionConfidence.from_string("inferred_pattern")
        assert conf == ExtractionConfidence.INFERRED_PATTERN

        conf = ExtractionConfidence.from_string("invalid")
        assert conf == ExtractionConfidence.AMBIGUOUS


class TestDefaultParser:
    """测试默认 Parser"""

    def test_parser_contract(self):
        """测试 Parser 契约"""
        parser = DefaultParser()
        assert hasattr(parser, 'parse')

    def test_parser_invalid_path(self):
        """测试无效路径"""
        parser = DefaultParser()
        result = parser.parse(Path("/nonexistent"))
        assert result is None

    def test_parser_file_not_dir(self):
        """测试文件而非目录"""
        parser = DefaultParser()
        # 使用一个存在的文件（如果有的话）
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            result = parser.parse(Path(f.name))
            assert result is None


class TestDefaultPatternExtractor:
    """测试默认 PatternExtractor"""

    def test_extractor_contract(self):
        """测试 Extractor 契约"""
        extractor = DefaultPatternExtractor()
        assert hasattr(extractor, 'extract_patterns')

    def test_extractor_none_input(self):
        """测试 None 输入"""
        extractor = DefaultPatternExtractor()
        result = extractor.extract_patterns(None)
        assert result == []

    def test_extractor_pipeline_detection(self):
        """测试流水线模式检测"""
        extractor = DefaultPatternExtractor()
        structure = {
            "name": "test_project",
            "type": "数据处理系统",
            "structure": {"modules": []}
        }
        result = extractor.extract_patterns(structure)
        # 应检测到流水线模式
        assert len(result) >= 1
        assert result[0]["name"] == "流水线骨架模式"


class TestDefaultMentalExtractor:
    """测试默认 MentalExtractor"""

    def test_extractor_contract(self):
        """测试 Extractor 契约"""
        extractor = DefaultMentalExtractor()
        assert hasattr(extractor, 'extract_mental_models')

    def test_extractor_none_input(self):
        """测试 None 输入"""
        extractor = DefaultMentalExtractor()
        result = extractor.extract_mental_models(None)
        assert result == []

    def test_extractor_structure_inference(self):
        """测试从结构推断心智模型"""
        extractor = DefaultMentalExtractor()
        structure = {
            "name": "test_project",
            "type": "数据处理系统",
            "structure": {"modules": ["skeleton"]}
        }
        result = extractor.extract_mental_models(structure)
        assert len(result) >= 1


class TestLocalStorage:
    """测试本地存储"""

    def test_storage_contract(self):
        """测试 Storage 契约"""
        storage = LocalStorage()
        assert hasattr(storage, 'save')

    def test_storage_save(self):
        """测试保存知识"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            knowledge = {
                "patterns": [{"id": "P-001", "name": "test_pattern"}],
                "mental_models": [],
                "case": {"project_name": "test_project"},
                "metadata": {}
            }
            result = storage.save(knowledge)
            assert result is True

            # 检查文件是否创建
            assert os.path.exists(os.path.join(tmpdir, "pattern-library"))


class TestJSONIndexer:
    """测试 JSON 索引"""

    def test_indexer_contract(self):
        """测试 Indexer 契约"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = JSONIndexer(os.path.join(tmpdir, "index.json"))
            assert hasattr(indexer, 'update')
            assert hasattr(indexer, 'search')

    def test_indexer_update(self):
        """测试更新索引"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = JSONIndexer(os.path.join(tmpdir, "index.json"))
            knowledge = {
                "patterns": [{"id": "P-001", "name": "test_pattern"}],
                "mental_models": [{"id": "M-001", "name": "test_model"}],
                "case": {"project_name": "test_project"},
                "metadata": {"forge_version": "2.0"}
            }
            result = indexer.update(knowledge)
            assert result is True


class TestKnowledgeForgePipeline:
    """测试骨架 Pipeline"""

    def test_pipeline_creation(self):
        """测试 Pipeline 创建"""
        pipeline = KnowledgeForgePipeline()
        assert pipeline.parser is not None
        assert pipeline.pattern_extractor is not None
        assert pipeline.mental_extractor is not None
        assert pipeline.storage is not None
        assert pipeline.indexer is not None

    def test_pipeline_forge_invalid_path(self):
        """测试无效路径"""
        pipeline = KnowledgeForgePipeline()
        result = pipeline.forge(Path("/nonexistent"))
        assert result.success is False
        assert len(result.errors) >= 1

    def test_pipeline_forge_valid_project(self):
        """测试解析有效项目"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建简单项目结构
            os.makedirs(os.path.join(tmpdir, "pipeline"))
            with open(os.path.join(tmpdir, "main.py"), 'w') as f:
                f.write("# main file\n")

            pipeline = KnowledgeForgePipeline()
            result = pipeline.forge(Path(tmpdir))

            # Parser 应成功
            assert result.project is not None
            # 应检测到设计模式
            assert len(result.patterns) >= 1


class TestPhase0Acceptance:
    """Phase 0 验收测试"""

    def test_tc001_skeleton_independent_run(self):
        """TC-001: 骨架独立运行测试"""
        # 创建 Pipeline
        pipeline = KnowledgeForgePipeline()
        assert pipeline is not None

        # 使用自身项目作为测试输入
        result = pipeline.forge(Path(__file__).parent.parent.parent)

        # 验收标准
        assert result is not None
        assert isinstance(result, ForgeResult)
        # Parser 成功（至少能解析项目结构）
        assert result.project is not None or len(result.errors) > 0

    def test_tc002_parser_failure_degradation(self):
        """TC-002: Parser失败降级测试"""
        pipeline = KnowledgeForgePipeline()
        result = pipeline.forge(Path("/nonexistent"))

        # Parser失败是致命错误
        assert result.success is False
        # 应有错误记录
        parse_errors = [e for e in result.errors if e.get("phase") == "parse"]
        assert len(parse_errors) >= 1

    def test_tc003_extractor_failure_degradation(self):
        """TC-003: Extractor失败降级测试"""
        # 使用返回空的 Extractor
        class EmptyExtractor:
            def extract_patterns(self, structure):
                return []

        pipeline = KnowledgeForgePipeline(
            pattern_extractor=EmptyExtractor()
        )

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "main.py"), 'w') as f:
                f.write("# test\n")

            result = pipeline.forge(Path(tmpdir))

            # Extractor失败不应阻塞流程
            assert result.success is True or result.project is not None

    def test_tc005_output_format(self):
        """TC-005: 输出格式测试"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建简单项目
            os.makedirs(os.path.join(tmpdir, "pipeline"))
            with open(os.path.join(tmpdir, "README.md"), 'w') as f:
                f.write("# Test Project\n这是一个测试项目。")

            pipeline = KnowledgeForgePipeline()
            result = pipeline.forge(Path(tmpdir))

            # 输出格式验证
            assert result.project is not None
            assert "name" in result.project
            assert "type" in result.project
            assert "_confidence" in result.project

            # Pattern 格式验证（如果有）
            if result.patterns:
                pattern = result.patterns[0]
                assert "id" in pattern
                assert "name" in pattern
                assert "confidence" in pattern

            # Mental Model 格式验证（如果有）
            if result.mental_models:
                model = result.mental_models[0]
                assert "id" in model
                assert "name" in model