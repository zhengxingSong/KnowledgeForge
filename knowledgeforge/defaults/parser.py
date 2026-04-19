"""
DefaultParser - 默认项目解析器

基于文件系统扫描的项目结构解析（Phase 0 基础版）。
Phase 1 将升级为 tree-sitter 驱动的解析器。
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from knowledgeforge.skeleton.contracts import ParserContract
from knowledgeforge.skeleton.confidence import ExtractionConfidence


class DefaultParser(ParserContract):
    """
    默认项目解析器

    Phase 0 基础版本：
    - 扫描目录结构
    - 检测文件类型和语言
    - 统计基本信息
    - 无 tree-sitter AST 解析

    输出置信度：EXTRACTED_STATIC（结构扫描）
    """

    # 忽略目录
    IGNORE_DIRS = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv',
        'dist', 'build', '.idea', '.vscode', 'target', 'bin',
        'obj', '.tox', '.pytest_cache', '.mypy_cache'
    }

    # 代码文件后缀映射语言
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.go': 'Go',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.rs': 'Rust',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C',
        '.hpp': 'C++',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.scala': 'Scala',
        '.lua': 'Lua',
        '.r': 'R',
        '.m': 'MATLAB',
        '.sh': 'Shell',
        '.bash': 'Shell',
    }

    # 入口文件模式
    ENTRY_POINT_PATTERNS = [
        'main.py', 'app.py', '__main__.py', 'server.py',
        'index.js', 'index.ts', 'app.js', 'app.ts',
        'main.go', 'main.rs', 'Main.java',
        'main.c', 'main.cpp',
    ]

    # 配置文件模式
    CONFIG_FILE_PATTERNS = [
        'config.yaml', 'config.yml', 'config.json', 'config.toml',
        'settings.py', 'settings.json',
        '.env', '.env.example',
        'pyproject.toml', 'setup.py', 'requirements.txt',
        'package.json', 'Cargo.toml', 'go.mod',
        'Makefile', 'Dockerfile', 'docker-compose.yml',
    ]

    def parse(self, project_path: Path, mode: str = "full") -> Optional[Dict]:
        """
        解析项目结构

        Args:
            project_path: 项目根目录路径
            mode: 解析模式（"full" | "incremental"）

        Returns:
            Optional[Dict]: 成功返回Structure Dict，失败返回None
        """
        start_time = time.time()

        try:
            # 1. 验证输入
            if not self._validate_input(project_path):
                return None

            # 2. 扫描目录
            all_files = self._scan_directory(project_path)

            # 3. 分类文件
            code_files, doc_files, config_files = self._classify_files(all_files)

            # 4. 检测主要语言
            language = self._detect_main_language(code_files)

            # 5. 检测系统类型
            system_type = self._detect_system_type(code_files, project_path)

            # 6. 检测模块
            modules = self._detect_modules(project_path)

            # 7. 检测入口点
            entry_points = self._find_entry_points(all_files)

            # 8. 计算统计
            stats = self._calculate_stats(all_files, code_files)

            # 9. 构建输出
            result = {
                "name": project_path.name,
                "type": system_type,
                "structure": {
                    "modules": modules,
                    "entry_points": entry_points,
                    "config_files": [str(f.relative_to(project_path)) for f in config_files],
                    "functions": [],  # Phase 1 实现
                    "classes": [],    # Phase 1 实现
                    "imports": []     # Phase 1 实现
                },
                "language": language,
                "stats": stats,
                "doc_files": [str(f.relative_to(project_path)) for f in doc_files],
                "_confidence": ExtractionConfidence.EXTRACTED_STATIC.value,
                "_parse_time_ms": int((time.time() - start_time) * 1000),
                "_parse_mode": mode,
                "_engine": "default-parser-v1",
                "_cache_hit": False
            }

            return result

        except Exception as e:
            print(f"[DefaultParser] 解析异常: {e}")
            return None

    def _validate_input(self, project_path: Path) -> bool:
        """验证输入路径"""
        if not project_path.exists():
            print(f"[DefaultParser] 路径不存在: {project_path}")
            return False
        if not project_path.is_dir():
            print(f"[DefaultParser] 不是目录: {project_path}")
            return False
        return True

    def _scan_directory(self, project_path: Path) -> List[Path]:
        """扫描目录获取所有文件"""
        files = []

        for root, dirs, filenames in os.walk(project_path):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS and not d.startswith('.')]

            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = Path(root) / filename
                    files.append(file_path)

        return files

    def _classify_files(self, files: List[Path]) -> tuple:
        """分类文件为代码、文档、配置"""
        code_files = []
        doc_files = []
        config_files = []

        doc_extensions = {'.md', '.rst', '.txt', '.doc', '.docx', '.pdf'}
        config_patterns = set(self.CONFIG_FILE_PATTERNS)

        for file_path in files:
            suffix = file_path.suffix.lower()
            name = file_path.name.lower()

            if name in config_patterns or name.startswith('config'):
                config_files.append(file_path)
            elif suffix in doc_extensions:
                doc_files.append(file_path)
            elif suffix in self.LANGUAGE_MAP:
                code_files.append(file_path)

        return code_files, doc_files, config_files

    def _detect_main_language(self, code_files: List[Path]) -> str:
        """检测主要语言"""
        if not code_files:
            return "未知"

        # 统计语言分布
        language_counts = {}
        for file_path in code_files:
            suffix = file_path.suffix.lower()
            language = self.LANGUAGE_MAP.get(suffix, "未知")
            language_counts[language] = language_counts.get(language, 0) + 1

        # 返回最多的语言
        if language_counts:
            return max(language_counts, key=language_counts.get)

        return "未知"

    def _detect_system_type(self, code_files: List[Path], project_path: Path) -> str:
        """检测系统类型"""
        # 检测数据处理系统特征
        pipeline_indicators = ['pipeline', 'flow', 'process', 'etl', 'batch', 'worker']
        api_indicators = ['api', 'route', 'controller', 'handler', 'endpoint', 'server']

        # 检测目录名
        dirs = [d.name.lower() for d in project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]

        has_pipeline = any(ind in d for d in dirs for ind in pipeline_indicators)
        has_api = any(ind in d for d in dirs for ind in api_indicators)

        if has_pipeline and has_api:
            return "混合系统"
        elif has_pipeline:
            return "数据处理系统"
        elif has_api:
            return "交互系统"

        # 检测文件名
        filenames = [f.name.lower() for f in code_files]
        has_pipeline_files = any(ind in fn for fn in filenames for ind in pipeline_indicators)
        has_api_files = any(ind in fn for fn in filenames for ind in api_indicators)

        if has_pipeline_files and has_api_files:
            return "混合系统"
        elif has_pipeline_files:
            return "数据处理系统"
        elif has_api_files:
            return "交互系统"

        return "未知"

    def _detect_modules(self, project_path: Path) -> List[str]:
        """检测模块"""
        modules = []

        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in self.IGNORE_DIRS:
                # 检查是否是Python包
                if (item / '__init__.py').exists():
                    modules.append(item.name)
                # 检查是否包含代码文件
                elif any(f.suffix in self.LANGUAGE_MAP for f in item.iterdir() if f.is_file()):
                    modules.append(item.name)

        return modules

    def _find_entry_points(self, files: List[Path]) -> List[str]:
        """查找入口文件"""
        entry_points = []

        for file_path in files:
            if file_path.name in self.ENTRY_POINT_PATTERNS:
                entry_points.append(file_path.name)

        return entry_points

    def _calculate_stats(self, all_files: List[Path], code_files: List[Path]) -> Dict:
        """计算统计信息"""
        total_lines = 0

        for file_path in code_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                total_lines += len(content.splitlines())
            except Exception:
                continue

        return {
            "files": len(all_files),
            "code_files": len(code_files),
            "lines": total_lines,
            "functions": 0,  # Phase 1 实现
            "classes": 0     # Phase 1 实现
        }