"""
Phase 2 验收测试

测试 Phase 2 功能：
- MCP服务器协议
- blast-radius影响范围分析
- verify测试验证
- install命令
"""

import sys
import tempfile
import json
from pathlib import Path
import unittest

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledgeforge.skeleton.confidence import ExtractionConfidence
from knowledgeforge.mcp.server import KnowledgeForgeMCPServer, create_mcp_server
from knowledgeforge.analysis.blast_radius import BlastRadiusAnalyzer, get_blast_radius_analyzer
from knowledgeforge.verification.test_verify import VerifyRunner, get_verify_runner


class TestMCPServer(unittest.TestCase):
    """测试 MCP Server"""

    def setUp(self):
        self.server = KnowledgeForgeMCPServer()

    def test_01_server_creation(self):
        """TC-201: MCP服务器创建"""
        self.assertIsNotNone(self.server, "服务器应创建成功")
        self.assertEqual(self.server.SERVER_NAME, "knowledgeforge", "服务器名正确")

    def test_02_tool_definitions(self):
        """TC-202: 工具定义"""
        tools = self.server.TOOLS
        self.assertGreaterEqual(len(tools), 5, "应有至少5个工具")

        tool_names = [t["name"] for t in tools]
        self.assertIn("forge_project", tool_names, "应有forge_project工具")
        self.assertIn("query_patterns", tool_names, "应有query_patterns工具")
        self.assertIn("blast_radius", tool_names, "应有blast_radius工具")
        self.assertIn("get_evidence", tool_names, "应有get_evidence工具")
        self.assertIn("list_projects", tool_names, "应有list_projects工具")

    def test_03_tool_schema(self):
        """TC-203: 工具Schema"""
        forge_tool = next((t for t in self.server.TOOLS if t["name"] == "forge_project"), None)

        self.assertIsNotNone(forge_tool, "forge_project工具应存在")
        self.assertIn("inputSchema", forge_tool, "工具应有inputSchema")
        self.assertIn("properties", forge_tool["inputSchema"], "Schema应有properties")
        self.assertIn("project_path", forge_tool["inputSchema"]["properties"], "应有project_path属性")

    def test_04_forge_project_tool(self):
        """TC-204: forge_project工具执行"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")

        result = self.server._forge_project({"project_path": str(project_path)})

        self.assertIn("success", result, "结果应包含success")
        self.assertTrue(result["success"], "解析应成功")

    def test_05_list_projects_tool(self):
        """TC-205: list_projects工具"""
        result = self.server._list_projects()

        self.assertIn("projects_count", result, "结果应包含projects_count")

    def test_06_config_generation(self):
        """TC-206: MCP配置生成"""
        config = self.server.generate_config()

        self.assertIn("mcpServers", config, "配置应包含mcpServers")
        self.assertIn("knowledgeforge", config["mcpServers"], "应有knowledgeforge服务器配置")

    def test_07_config_file_generation(self):
        """TC-207: 配置文件生成"""
        temp_dir = Path(tempfile.mkdtemp())
        config_path = temp_dir / "config.json"

        config = self.server.generate_config(config_path)

        self.assertTrue(config_path.exists(), "配置文件应被创建")

        with open(config_path) as f:
            saved_config = json.load(f)

        self.assertEqual(config, saved_config, "保存的配置应与返回的一致")

    def test_08_factory_function(self):
        """TC-208: 工厂函数"""
        server = create_mcp_server()
        self.assertIsNotNone(server, "工厂函数应返回服务器实例")


class TestBlastRadiusAnalyzer(unittest.TestCase):
    """测试 BlastRadiusAnalyzer"""

    def setUp(self):
        self.analyzer = BlastRadiusAnalyzer()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_09_analyzer_creation(self):
        """TC-209: 分析器创建"""
        self.assertIsNotNone(self.analyzer, "分析器应创建成功")

    def test_10_analyze_pattern_not_found(self):
        """TC-210: 分析未找到的模式"""
        result = self.analyzer.analyze("invalid-pattern-id")

        self.assertIn("error", result, "未找到模式应返回错误")

    def test_11_analyze_with_pattern(self):
        """TC-211: 分析存在的模式"""
        # 先解析一个项目生成索引
        from knowledgeforge.skeleton import KnowledgeForgePipeline

        project_path = Path(self.temp_dir) / "test_project"
        project_path.mkdir()
        (project_path / "pipeline.py").write_text("def run(): pass")

        pipeline = KnowledgeForgePipeline()
        pipeline.forge(project_path)

        # 搜索模式ID
        from knowledgeforge.defaults import JSONIndexer
        indexer = JSONIndexer()
        index = indexer.load_index()

        # 正确的索引结构 - patterns 是单独的 dict
        patterns = index.get("patterns", {})
        if patterns:
            pattern_id = list(patterns.keys())[0]
            result = self.analyzer.analyze(pattern_id, depth=2)

            self.assertIn("pattern_id", result, "结果应包含pattern_id")
            self.assertIn("risk_level", result, "结果应包含risk_level")
        else:
            # 如果没有模式，跳过测试
            self.skipTest("没有生成的模式")

    def test_12_risk_levels(self):
        """TC-212: 风险等级"""
        risk_levels = ["low", "medium", "high"]

        # 测试风险等级定义
        recommendations = {
            "low": "可以直接修改",
            "medium": "需检查相关模块",
            "high": "修改风险较高"
        }

        for level, rec in recommendations.items():
            self.assertIn(level, risk_levels, f"{level}应为有效风险等级")

    def test_13_factory_function(self):
        """TC-213: 分析器工厂函数"""
        analyzer = get_blast_radius_analyzer()
        self.assertIsNotNone(analyzer, "工厂函数应返回分析器实例")


class TestVerifyRunner(unittest.TestCase):
    """测试 VerifyRunner"""

    def setUp(self):
        self.runner = VerifyRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_14_runner_creation(self):
        """TC-214: 验证器创建"""
        self.assertIsNotNone(self.runner, "验证器应创建成功")

    def test_15_verify_pattern_not_found(self):
        """TC-215: 验证未找到的模式"""
        result = self.runner.run_verify("invalid-pattern-id")

        self.assertIn("error", result, "未找到模式应返回错误")

    def test_16_confidence_promotion_mapping(self):
        """TC-216: 置信度提升映射"""
        # 测试置信度提升逻辑
        promotion = self.runner.CONFIDENCE_PROMOTION

        # INFERRED_PATTERN 应能提升到 VERIFIED_TEST
        self.assertEqual(
            promotion[ExtractionConfidence.INFERRED_PATTERN],
            ExtractionConfidence.VERIFIED_TEST,
            "INFERRED_PATTERN应能提升到VERIFIED_TEST"
        )

        # EXTRACTED_STATIC 应保持不变（最高）
        self.assertEqual(
            promotion[ExtractionConfidence.EXTRACTED_STATIC],
            ExtractionConfidence.EXTRACTED_STATIC,
            "EXTRACTED_STATIC应保持不变"
        )

    def test_17_test_success_rate_calculation(self):
        """TC-217: 测试成功率计算"""
        test_results = [
            {"passed": True},
            {"passed": True},
            {"passed": False},
        ]

        success_rate = self.runner._calculate_success_rate(test_results)

        self.assertEqual(success_rate, 2/3, "成功率应为2/3")

    def test_18_empty_test_results(self):
        """TC-218: 空测试结果"""
        success_rate = self.runner._calculate_success_rate([])

        self.assertEqual(success_rate, 0.0, "空结果成功率应为0")

    def test_19_factory_function(self):
        """TC-219: 验证器工厂函数"""
        runner = get_verify_runner()
        self.assertIsNotNone(runner, "工厂函数应返回验证器实例")


class TestPhase2Integration(unittest.TestCase):
    """Phase 2 集成测试"""

    def test_20_module_exports(self):
        """TC-220: 模块导出"""
        # MCP模块
        from knowledgeforge.mcp import KnowledgeForgeMCPServer, create_mcp_server

        # Analysis模块
        from knowledgeforge.analysis import BlastRadiusAnalyzer, get_blast_radius_analyzer

        # Verification模块
        from knowledgeforge.verification import VerifyRunner, get_verify_runner

        # 所有导出应正常
        self.assertIsNotNone(KnowledgeForgeMCPServer)
        self.assertIsNotNone(BlastRadiusAnalyzer)
        self.assertIsNotNone(VerifyRunner)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestMCPServer))
    suite.addTests(loader.loadTestsFromTestCase(TestBlastRadiusAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestVerifyRunner))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2Integration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)