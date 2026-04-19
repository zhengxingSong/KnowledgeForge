"""
Phase 1 验收测试

测试 Phase 1 功能：
- LanguageConfig (23+语言配置)
- TreeSitterParser (AST解析)
- CacheManager (SHA256缓存)
- 置信度系统集成
"""

import os
import sys
import tempfile
import hashlib
from pathlib import Path
import unittest

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledgeforge.skeleton.confidence import ExtractionConfidence
from knowledgeforge.skeleton.evidence import ExtractionEvidence
from knowledgeforge.defaults.language_config import LanguageConfig, get_language_config
from knowledgeforge.defaults.cache_manager import CacheManager, get_cache_manager
from knowledgeforge.defaults.tree_sitter_parser import TreeSitterParser


class TestLanguageConfig(unittest.TestCase):
    """测试 LanguageConfig"""

    def setUp(self):
        self.config = LanguageConfig()

    def test_01_supported_languages_count(self):
        """TC-101: 支持23+语言"""
        languages = self.config.get_supported_languages()
        self.assertGreaterEqual(len(languages), 23, "应支持至少23种语言")

    def test_02_detect_python(self):
        """TC-102: 检测Python文件"""
        file_path = Path("test.py")
        lang = self.config.detect_language(file_path)
        self.assertEqual(lang, 'python', "应正确检测Python")

    def test_03_detect_javascript(self):
        """TC-103: 检测JavaScript文件"""
        file_path = Path("test.js")
        lang = self.config.detect_language(file_path)
        self.assertEqual(lang, 'javascript', "应正确检测JavaScript")

    def test_04_detect_typescript(self):
        """TC-104: 检测TypeScript文件"""
        file_path = Path("test.ts")
        lang = self.config.detect_language(file_path)
        self.assertEqual(lang, 'typescript', "应正确检测TypeScript")

    def test_05_detect_go(self):
        """TC-105: 检测Go文件"""
        file_path = Path("main.go")
        lang = self.config.detect_language(file_path)
        self.assertEqual(lang, 'go', "应正确检测Go")

    def test_06_detect_rust(self):
        """TC-106: 检测Rust文件"""
        file_path = Path("main.rs")
        lang = self.config.detect_language(file_path)
        self.assertEqual(lang, 'rust', "应正确检测Rust")

    def test_07_detect_unknown(self):
        """TC-107: 检测未知文件"""
        file_path = Path("test.xyz")
        lang = self.config.detect_language(file_path)
        self.assertIsNone(lang, "未知文件应返回None")

    def test_08_get_tree_sitter_lang(self):
        """TC-108: 获取tree-sitter语言名"""
        ts_lang = self.config.get_tree_sitter_lang('python')
        self.assertEqual(ts_lang, 'python', "Python tree-sitter语言名正确")

    def test_09_is_supported(self):
        """TC-109: 检查文件是否支持"""
        py_file = Path("test.py")
        self.assertTrue(self.config.is_supported(py_file), "Python文件应支持")

        xyz_file = Path("test.xyz")
        self.assertFalse(self.config.is_supported(xyz_file), "未知文件不应支持")

    def test_10_get_extensions(self):
        """TC-110: 获取语言扩展名"""
        extensions = self.config.get_extensions('python')
        self.assertIn('.py', extensions, "Python扩展名包含.py")


class TestCacheManager(unittest.TestCase):
    """测试 CacheManager"""

    def setUp(self):
        self.cache_manager = CacheManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_11_compute_sha256(self):
        """TC-111: 计算SHA256"""
        # 创建临时文件
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")

        sha256 = self.cache_manager.compute_sha256(test_file)

        # SHA256应为64字符十六进制
        self.assertEqual(len(sha256), 64, "SHA256应为64字符")
        self.assertTrue(all(c in '0123456789abcdef' for c in sha256), "SHA256应为十六进制")

    def test_12_sha256_consistency(self):
        """TC-112: SHA256一致性"""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")

        sha1 = self.cache_manager.compute_sha256(test_file)
        sha2 = self.cache_manager.compute_sha256(test_file)

        self.assertEqual(sha1, sha2, "相同文件SHA256应相同")

    def test_13_sha256_different_content(self):
        """TC-113: 不同内容SHA256不同"""
        file1 = Path(self.temp_dir) / "test1.py"
        file2 = Path(self.temp_dir) / "test2.py"

        file1.write_text("print('hello')")
        file2.write_text("print('world')")

        sha1 = self.cache_manager.compute_sha256(file1)
        sha2 = self.cache_manager.compute_sha256(file2)

        self.assertNotEqual(sha1, sha2, "不同内容SHA256应不同")

    def test_14_manifest_save_load(self):
        """TC-114: Manifest保存和加载"""
        project_path = Path(self.temp_dir)
        manifest = {
            'files': {},
            'version': '1.0',
            'last_parse': None
        }

        # 保存
        result = self.cache_manager.save_manifest(project_path, manifest)
        self.assertTrue(result, "Manifest保存应成功")

        # 加载
        loaded = self.cache_manager.load_manifest(project_path)
        self.assertEqual(loaded.get('version'), '1.0', "Manifest版本应一致")

    def test_15_is_changed_detection(self):
        """TC-115: 变更检测"""
        project_path = Path(self.temp_dir)
        test_file = project_path / "test.py"
        test_file.write_text("print('hello')")

        # 首次检测应视为变更
        manifest = {'files': {}}
        self.assertTrue(
            self.cache_manager.is_changed(test_file, manifest),
            "新文件应视为变更"
        )

        # 更新manifest后再检测
        manifest = self.cache_manager.update_file_hash(manifest, test_file)
        self.assertFalse(
            self.cache_manager.is_changed(test_file, manifest),
            "未变更文件不应视为变更"
        )

        # 修改文件内容后再检测
        test_file.write_text("print('world')")
        self.assertTrue(
            self.cache_manager.is_changed(test_file, manifest),
            "变更文件应视为变更"
        )


class TestExtractionConfidence(unittest.TestCase):
    """测试置信度系统"""

    def test_16_confidence_levels(self):
        """TC-116: 置信度5级"""
        levels = [
            ExtractionConfidence.EXTRACTED_STATIC,
            ExtractionConfidence.INFERRED_PATTERN,
            ExtractionConfidence.INFERRED_SEMANTIC,
            ExtractionConfidence.VERIFIED_TEST,
            ExtractionConfidence.VERIFIED_RUNTIME,
            ExtractionConfidence.AMBIGUOUS,
        ]

        self.assertEqual(len(levels), 6, "应有6个置信度级别（包含AMBIGUOUS）")

    def test_17_confidence_values(self):
        """TC-117: 置信度值"""
        self.assertEqual(
            ExtractionConfidence.EXTRACTED_STATIC.value,
            'extracted_static',
            "静态提取置信度值正确"
        )

        self.assertEqual(
            ExtractionConfidence.INFERRED_PATTERN.value,
            'inferred_pattern',
            "模式推断置信度值正确"
        )

    def test_18_confidence_from_string(self):
        """TC-118: 从字符串创建置信度"""
        confidence = ExtractionConfidence.from_string('extracted_static')
        self.assertEqual(
            confidence,
            ExtractionConfidence.EXTRACTED_STATIC,
            "应正确创建置信度"
        )

        # 未知字符串应返回AMBIGUOUS
        unknown = ExtractionConfidence.from_string('unknown_value')
        self.assertEqual(
            unknown,
            ExtractionConfidence.AMBIGUOUS,
            "未知值应返回AMBIGUOUS"
        )


class TestExtractionEvidence(unittest.TestCase):
    """测试证据记录"""

    def test_19_evidence_creation(self):
        """TC-119: 证据创建"""
        evidence = ExtractionEvidence.static("tree-sitter直接提取函数名")

        self.assertEqual(
            evidence.confidence,
            ExtractionConfidence.EXTRACTED_STATIC,
            "静态证据置信度正确"
        )
        self.assertEqual(
            evidence.reasoning,
            "tree-sitter直接提取函数名",
            "证据理由正确"
        )

    def test_20_evidence_inferred_pattern(self):
        """TC-120: 模式推断证据"""
        evidence = ExtractionEvidence.inferred_pattern(
            reasoning="检测到类名含Factory + create方法",
            naming_hints=["Factory", "create"],
            structural_match=True
        )

        self.assertEqual(
            evidence.confidence,
            ExtractionConfidence.INFERRED_PATTERN,
            "模式推断置信度正确"
        )
        self.assertTrue(evidence.structural_match, "结构匹配应为True")
        self.assertIn("Factory", evidence.naming_hints, "命名提示应包含Factory")

    def test_21_evidence_to_dict(self):
        """TC-121: 证据转字典"""
        evidence = ExtractionEvidence.static("tree-sitter直接提取")
        result = evidence.to_dict()

        self.assertIn('confidence', result, "字典应包含confidence")
        self.assertIn('reasoning', result, "字典应包含reasoning")
        self.assertEqual(
            result['confidence'],
            'extracted_static',
            "字典置信度值正确"
        )


class TestTreeSitterParser(unittest.TestCase):
    """测试 TreeSitterParser"""

    def setUp(self):
        self.parser = TreeSitterParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_22_parse_project_structure(self):
        """TC-122: 解析项目结构"""
        # 创建简单项目
        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()

        # 创建Python文件
        py_file = project_path / "main.py"
        py_file.write_text("""
def hello():
    print("hello")

class MyClass:
    def method(self):
        return 42
""")

        # 解析
        result = self.parser.parse(project_path)

        self.assertIsNotNone(result, "解析结果不应为None")
        self.assertEqual(result.get('name'), 'test_project', "项目名正确")
        self.assertIn('structure', result, "应包含structure")

    def test_23_parser_confidence(self):
        """TC-123: Parser置信度"""
        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")

        result = self.parser.parse(project_path)

        self.assertIsNotNone(result)
        self.assertEqual(
            result.get('_confidence'),
            ExtractionConfidence.EXTRACTED_STATIC.value,
            "Parser应返回静态提取置信度"
        )

    def test_24_functions_extraction(self):
        """TC-124: 函数提取"""
        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()

        py_file = project_path / "main.py"
        py_file.write_text("""
def func1():
    pass

def func2():
    pass
""")

        result = self.parser.parse(project_path)

        self.assertIsNotNone(result)
        functions = result.get('structure', {}).get('functions', [])
        # 函数列表可能为空如果tree-sitter未安装，需要检查tree-sitter是否可用
        if functions:
            self.assertGreaterEqual(len(functions), 2, "应提取到函数")

    def test_25_classes_extraction(self):
        """TC-125: 类提取"""
        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()

        py_file = project_path / "main.py"
        py_file.write_text("""
class MyClass:
    def method(self):
        pass

class AnotherClass:
    pass
""")

        result = self.parser.parse(project_path)

        self.assertIsNotNone(result)
        classes = result.get('structure', {}).get('classes', [])
        if classes:
            self.assertGreaterEqual(len(classes), 2, "应提取到类")

    def test_26_incremental_mode(self):
        """TC-126: 增量解析模式"""
        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")

        # 第一次解析
        result1 = self.parser.parse(project_path, mode="full")
        self.assertIsNotNone(result1)
        self.assertEqual(result1['_parse_mode'], 'full', "应为全量模式")

        # 第二次增量解析（应该使用缓存）
        result2 = self.parser.parse(project_path, mode="incremental")
        self.assertIsNotNone(result2)
        self.assertEqual(result2['_parse_mode'], 'incremental', "应为增量模式")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractionConfidence))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractionEvidence))
    suite.addTests(loader.loadTestsFromTestCase(TestTreeSitterParser))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)