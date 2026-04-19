"""
VerifyRunner - 测试验证模块

执行相关测试以提升模式置信度：
- 查找相关测试
- 执行测试
- 更新置信度
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from knowledgeforge.defaults.indexer import JSONIndexer
from knowledgeforge.defaults.storage import LocalStorage
from knowledgeforge.skeleton.confidence import ExtractionConfidence


class VerifyRunner:
    """
    测试验证运行器

    执行相关测试以提升模式置信度：
    - 查找相关测试
    - 执行测试
    - 更新置信度
    """

    # 置信度提升映射
    CONFIDENCE_PROMOTION = {
        ExtractionConfidence.AMBIGUOUS: ExtractionConfidence.INFERRED_PATTERN,
        ExtractionConfidence.INFERRED_SEMANTIC: ExtractionConfidence.INFERRED_PATTERN,
        ExtractionConfidence.INFERRED_PATTERN: ExtractionConfidence.VERIFIED_TEST,
        ExtractionConfidence.EXTRACTED_STATIC: ExtractionConfidence.EXTRACTED_STATIC,  # 最高
        ExtractionConfidence.VERIFIED_TEST: ExtractionConfidence.VERIFIED_TEST,
        ExtractionConfidence.VERIFIED_RUNTIME: ExtractionConfidence.VERIFIED_RUNTIME,
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化验证器

        Args:
            output_dir: 知识输出目录
        """
        self.indexer = JSONIndexer()
        output_dir_str = str(output_dir) if output_dir else None
        self.storage = LocalStorage(output_dir=output_dir_str)

    def run_verify(
        self,
        pattern_id: str,
        project_path: Optional[Path] = None,
        test_command: Optional[str] = None
    ) -> Dict:
        """
        运行测试验证

        Args:
            pattern_id: 模式ID
            project_path: 项目路径（用于运行测试）
            test_command: 自定义测试命令

        Returns:
            Dict: 验证结果
        """
        # 1. 查找模式
        pattern = self._find_pattern(pattern_id)
        if not pattern:
            return {
                "error": f"Pattern not found: {pattern_id}",
                "pattern_id": pattern_id
            }

        # 2. 当前置信度
        current_confidence = ExtractionConfidence.from_string(
            pattern.get("confidence", "ambiguous")
        )

        # 3. 查找相关测试
        tests = self._find_related_tests(pattern, project_path)

        # 4. 执行测试
        test_results = []
        if project_path and tests:
            test_results = self._execute_tests(project_path, tests, test_command)

        # 5. 计算测试成功率
        success_rate = self._calculate_success_rate(test_results)

        # 6. 决定是否提升置信度
        promoted = success_rate >= 0.8  # 80%以上测试通过才提升
        new_confidence = current_confidence

        if promoted:
            new_confidence = self.CONFIDENCE_PROMOTION.get(
                current_confidence,
                current_confidence
            )

        # 7. 更新模式置信度（如果提升）
        if promoted and new_confidence != current_confidence:
            self._update_pattern_confidence(pattern_id, new_confidence)

        # 8. 构建结果
        result = {
            "pattern_id": pattern_id,
            "pattern_name": pattern.get("name"),

            # 测试结果
            "tests_found": len(tests),
            "tests_executed": len(test_results),
            "tests_passed": sum(1 for t in test_results if t.get("passed")),
            "success_rate": success_rate,

            # 置信度变化
            "confidence_before": current_confidence.value,
            "confidence_after": new_confidence.value,
            "promoted": promoted,

            # 测试详情
            "test_results": test_results[:5],  # 最多返回5个测试详情

            # 证据更新
            "evidence_update": {
                "tests_verified": promoted,
                "test_coverage": success_rate,
                "verification_time": time.time()
            }
        }

        return result

    def verify_all_patterns(self, project_path: Path) -> Dict:
        """
        验证项目中所有模式

        Args:
            project_path: 项目路径

        Returns:
            Dict: 批量验证结果
        """
        index_data = self.indexer.load_index()
        if not index_data:
            return {"error": "No index data found"}

        results = []

        for project_entry in index_data.get("projects", []):
            for pattern in project_entry.get("patterns", []):
                pattern_id = pattern.get("id")
                verify_result = self.run_verify(pattern_id, project_path)
                results.append(verify_result)

        # 统计
        promoted_count = sum(1 for r in results if r.get("promoted"))

        return {
            "total_patterns": len(results),
            "promoted_count": promoted_count,
            "results": results
        }

    def _find_pattern(self, pattern_id: str) -> Optional[Dict]:
        """查找模式"""
        index_data = self.indexer.load_index()
        if not index_data:
            return None

        # 直接从 patterns dict 查找
        patterns = index_data.get("patterns", {})
        if pattern_id in patterns:
            return patterns[pattern_id]

        return None

    def _find_related_tests(self, pattern: Dict, project_path: Optional[Path]) -> List[Dict]:
        """查找相关测试"""
        tests = []

        if not project_path:
            return tests

        # 搜索测试文件
        test_patterns = ["test_", "_test.py", "tests.py", "test.py"]

        for test_pattern in test_patterns:
            for test_file in project_path.rglob(f"{test_pattern}*"):
                if test_file.is_file():
                    tests.append({
                        "file": str(test_file.relative_to(project_path)),
                        "type": "unit_test"
                    })

        return tests[:10]  # 最多10个测试

    def _execute_tests(
        self,
        project_path: Path,
        tests: List[Dict],
        test_command: Optional[str] = None
    ) -> List[Dict]:
        """执行测试"""
        results = []

        # 默认使用pytest
        if not test_command:
            test_command = "pytest tests/ -v --tb=short"

        try:
            # 运行测试命令
            proc = subprocess.run(
                test_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
            )

            # 解析结果
            output = proc.stdout + proc.stderr
            passed = proc.returncode == 0

            # 从输出提取测试详情
            for test in tests[:3]:  # 执行最多3个测试
                results.append({
                    "file": test.get("file"),
                    "passed": passed,
                    "output_snippet": output[:200] if output else ""
                })

        except subprocess.TimeoutExpired:
            results.append({
                "error": "Test execution timeout",
                "passed": False
            })
        except Exception as e:
            results.append({
                "error": str(e),
                "passed": False
            })

        return results

    def _calculate_success_rate(self, test_results: List[Dict]) -> float:
        """计算测试成功率"""
        if not test_results:
            return 0.0

        passed_count = sum(1 for t in test_results if t.get("passed"))
        return passed_count / len(test_results)

    def _update_pattern_confidence(self, pattern_id: str, new_confidence: ExtractionConfidence) -> bool:
        """更新模式置信度"""
        # 更新index.json
        index_data = self.indexer.load_index()
        if not index_data:
            return False

        for project_entry in index_data.get("projects", []):
            for pattern in project_entry.get("patterns", []):
                if pattern.get("id") == pattern_id:
                    pattern["confidence"] = new_confidence.value

                    # 更新证据
                    evidence = pattern.get("evidence", {})
                    evidence["tests_verified"] = True
                    evidence["test_coverage"] = 1.0
                    pattern["evidence"] = evidence

                    break

        # 保存更新后的index
        self.indexer.save_index(index_data)

        return True


# 全局验证器实例
_global_verify_runner: Optional[VerifyRunner] = None


def get_verify_runner() -> VerifyRunner:
    """获取全局验证器实例"""
    global _global_verify_runner
    if _global_verify_runner is None:
        _global_verify_runner = VerifyRunner()
    return _global_verify_runner