"""
TreeSitterParser - Tree-sitter AST 解析器

基于 tree-sitter 的零LLM消耗 AST 解析。
支持 23+ 编程语言。
"""

import importlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from knowledgeforge.skeleton.contracts import ParserContract
from knowledgeforge.skeleton.confidence import ExtractionConfidence
from knowledgeforge.defaults.language_config import get_language_config, LanguageConfig
from knowledgeforge.defaults.cache_manager import get_cache_manager, CacheManager


class TreeSitterParser(ParserContract):
    """
    Tree-sitter AST 解析器

    Phase 1 核心功能：
    - 使用 tree-sitter 解析 AST
    - 零 LLM 消耗
    - 支持 23+ 语言
    - 提取函数、类、import 等结构
    - SHA256 缓存支持增量解析
    """

    # tree-sitter 语言包映射
    TREE_SITTER_LANG_PACKAGES: Dict[str, str] = {
        'python': 'tree_sitter_python',
        'javascript': 'tree_sitter_javascript',
        'typescript': 'tree_sitter_typescript',
        'tsx': 'tree_sitter_tsx',
        'jsx': 'tree_sitter_jsx',
        'go': 'tree_sitter_go',
        'rust': 'tree_sitter_rust',
        'java': 'tree_sitter_java',
        'kotlin': 'tree_sitter_kotlin',
        'c': 'tree_sitter_c',
        'cpp': 'tree_sitter_cpp',
        'ruby': 'tree_sitter_ruby',
        'php': 'tree_sitter_php',
        'swift': 'tree_sitter_swift',
        'scala': 'tree_sitter_scala',
        'lua': 'tree_sitter_lua',
        'r': 'tree_sitter_r',
        'bash': 'tree_sitter_bash',
        'json': 'tree_sitter_json',
        'yaml': 'tree_sitter_yaml',
        'toml': 'tree_sitter_toml',
        'html': 'tree_sitter_html',
        'css': 'tree_sitter_css',
        'markdown': 'tree_sitter_markdown',
    }

    # 忽略目录
    IGNORE_DIRS = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv',
        'dist', 'build', '.idea', '.vscode', 'target', 'bin',
        'obj', '.tox', '.pytest_cache', '.mypy_cache',
        '.knowledgeforge', 'knowledge_output'
    }

    def __init__(
        self,
        language_config: Optional[LanguageConfig] = None,
        cache_manager: Optional[CacheManager] = None,
        use_cache: bool = True
    ):
        """
        初始化解析器

        Args:
            language_config: 语言配置
            cache_manager: 缓存管理器
            use_cache: 是否使用缓存
        """
        self.language_config = language_config or get_language_config()
        self.cache_manager = cache_manager or get_cache_manager()
        self.use_cache = use_cache

        # 已加载的 Parser 实例缓存
        self._parsers: Dict[str, Any] = {}
        self._languages: Dict[str, Any] = {}

    def parse(self, project_path: Path, mode: str = "full") -> Optional[Dict]:
        """
        解析项目结构

        Args:
            project_path: 项目根目录路径
            mode: 解析模式（"full" | "incremental"）

        Returns:
            Optional[Dict]: 成功返回 Structure Dict，失败返回 None
        """
        start_time = time.time()

        try:
            # 1. 验证输入
            if not self._validate_input(project_path):
                return None

            # 2. 检查缓存（incremental mode）
            if mode == "incremental" and self.use_cache:
                cached_result = self.cache_manager.load_result(project_path)
                if cached_result and cached_result.success:
                    cached_result.parse_metadata['_cache_hit'] = True
                    return cached_result.project

            # 3. 扫描目录
            all_files = self._scan_directory(project_path)

            # 4. 检测变更文件（incremental mode）
            if mode == "incremental" and self.use_cache:
                manifest = self.cache_manager.load_manifest(project_path)
                changed_files = self.cache_manager.detect_changes(project_path, all_files)
            else:
                changed_files = all_files

            # 5. 分类文件
            code_files, doc_files, config_files = self._classify_files(all_files)

            # 6. 解析代码文件 AST
            functions, classes, imports = self._parse_code_files(changed_files)

            # 7. 检测主要语言
            language = self._detect_main_language(code_files)

            # 8. 检测系统类型
            system_type = self._detect_system_type(code_files, project_path)

            # 9. 检测模块
            modules = self._detect_modules(project_path)

            # 10. 检测入口点
            entry_points = self._find_entry_points(all_files)

            # 11. 计算统计
            stats = self._calculate_stats(all_files, code_files, functions, classes)

            # 12. 构建输出
            result = {
                "name": project_path.name,
                "type": system_type,
                "structure": {
                    "modules": modules,
                    "entry_points": entry_points,
                    "config_files": [str(f.relative_to(project_path)) for f in config_files],
                    "functions": functions,
                    "classes": classes,
                    "imports": imports
                },
                "language": language,
                "stats": stats,
                "doc_files": [str(f.relative_to(project_path)) for f in doc_files],
                "_confidence": ExtractionConfidence.EXTRACTED_STATIC.value,
                "_parse_time_ms": int((time.time() - start_time) * 1000),
                "_parse_mode": mode,
                "_engine": "tree-sitter-parser-v1",
                "_cache_hit": False,
                "_files_parsed": len(changed_files),
                "_files_cached": len(all_files) - len(changed_files) if mode == "incremental" else 0
            }

            # 13. 更新缓存
            if self.use_cache:
                manifest = self.cache_manager.load_manifest(project_path)
                for file_path in changed_files:
                    self.cache_manager.update_file_hash(manifest, file_path)
                manifest['last_parse'] = time.time()
                self.cache_manager.save_manifest(project_path, manifest)

            return result

        except Exception as e:
            print(f"[TreeSitterParser] 解析异常: {e}")
            return None

    def parse_file(self, file_path: Path) -> Dict:
        """
        解析单个文件 AST

        Args:
            file_path: 文件路径

        Returns:
            Dict: AST 结构信息
        """
        # 1. 检测语言
        language_name = self.language_config.detect_language(file_path)
        if not language_name:
            return {"error": "unknown_language", "file": str(file_path)}

        # 2. 获取 tree-sitter 语言
        tree_sitter_lang = self.language_config.get_tree_sitter_lang(language_name)
        if not tree_sitter_lang:
            return {"error": "no_tree_sitter_support", "language": language_name}

        # 3. 加载 Parser
        parser = self._load_parser(tree_sitter_lang)
        if not parser:
            return {"error": "parser_load_failed", "language": language_name}

        # 4. 读取文件内容
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": "read_failed", "file": str(file_path), "reason": str(e)}

        # 5. 解析 AST
        tree = parser.parse(bytes(content, 'utf-8'))

        # 6. 提取结构信息
        result = self._extract_structure(tree.root_node, language_name)

        result['_file'] = str(file_path)
        result['_language'] = language_name
        result['_confidence'] = ExtractionConfidence.EXTRACTED_STATIC.value

        return result

    def _validate_input(self, project_path: Path) -> bool:
        """验证输入路径"""
        if not project_path.exists():
            print(f"[TreeSitterParser] 路径不存在: {project_path}")
            return False
        if not project_path.is_dir():
            print(f"[TreeSitterParser] 不是目录: {project_path}")
            return False
        return True

    def _scan_directory(self, project_path: Path) -> List[Path]:
        """扫描目录获取所有文件"""
        files = []

        for root, dirs, filenames in project_path.walk():
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
        config_patterns = {
            'config.yaml', 'config.yml', 'config.json', 'config.toml',
            'settings.py', 'settings.json',
            '.env', '.env.example',
            'pyproject.toml', 'setup.py', 'requirements.txt',
            'package.json', 'Cargo.toml', 'go.mod',
            'Makefile', 'Dockerfile', 'docker-compose.yml',
        }

        for file_path in files:
            suffix = file_path.suffix.lower()
            name = file_path.name.lower()

            if name in config_patterns or name.startswith('config'):
                config_files.append(file_path)
            elif suffix in doc_extensions:
                doc_files.append(file_path)
            elif self.language_config.is_supported(file_path):
                code_files.append(file_path)

        return code_files, doc_files, config_files

    def _load_parser(self, tree_sitter_lang: str) -> Optional[Any]:
        """加载 tree-sitter Parser"""
        # 检查缓存
        if tree_sitter_lang in self._parsers:
            return self._parsers[tree_sitter_lang]

        # 查找语言包名称
        package_name = self.TREE_SITTER_LANG_PACKAGES.get(tree_sitter_lang)
        if not package_name:
            return None

        # 动态加载语言包
        try:
            lang_module = importlib.import_module(package_name)
            language = lang_module.language()

            # 创建 Parser
            import tree_sitter
            parser = tree_sitter.Parser(language)

            # 缓存
            self._parsers[tree_sitter_lang] = parser
            self._languages[tree_sitter_lang] = language

            return parser
        except ImportError:
            print(f"[TreeSitterParser] 语言包未安装: {package_name}")
            return None
        except Exception as e:
            print(f"[TreeSitterParser] 加载语言包失败: {e}")
            return None

    def _extract_structure(self, node: Any, language: str) -> Dict:
        """
        从 AST 节点提取结构信息

        Args:
            node: tree-sitter AST 节点
            language: 语言名称

        Returns:
            Dict: 结构信息
        """
        functions = []
        classes = []
        imports = []

        # 遍历 AST
        self._walk_ast(node, functions, classes, imports, language)

        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "_node_count": node.child_count
        }

    def _walk_ast(
        self,
        node: Any,
        functions: List,
        classes: List,
        imports: List,
        language: str
    ) -> None:
        """遍历 AST 提取信息"""

        # 根据语言选择节点类型
        if language == 'python':
            self._walk_python_ast(node, functions, classes, imports)
        elif language in ['javascript', 'typescript', 'jsx', 'tsx']:
            self._walk_js_ast(node, functions, classes, imports)
        elif language == 'go':
            self._walk_go_ast(node, functions, classes, imports)
        elif language == 'rust':
            self._walk_rust_ast(node, functions, classes, imports)
        elif language == 'java':
            self._walk_java_ast(node, functions, classes, imports)
        elif language in ['c', 'cpp']:
            self._walk_c_ast(node, functions, classes, imports)
        else:
            # 通用遍历
            self._walk_generic_ast(node, functions, classes, imports)

    def _walk_python_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 Python AST"""
        for child in node.children:
            if child.type == 'function_definition':
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'function',
                        'start_line': child.start_point[0] + 1,
                        'end_line': child.end_point[0] + 1,
                    })

            elif child.type == 'class_definition':
                name_node = child.child_by_field_name('name')
                if name_node:
                    class_name = name_node.text.decode('utf-8')
                    methods = []
                    # 提取类方法
                    body = child.child_by_field_name('body')
                    if body:
                        for method in body.children:
                            if method.type == 'function_definition':
                                method_name = method.child_by_field_name('name')
                                if method_name:
                                    methods.append(method_name.text.decode('utf-8'))

                    classes.append({
                        'name': class_name,
                        'type': 'class',
                        'methods': methods,
                        'start_line': child.start_point[0] + 1,
                        'end_line': child.end_point[0] + 1,
                    })

            elif child.type in ['import_statement', 'import_from_statement']:
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'import',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_python_ast(child, functions, classes, imports)

    def _walk_js_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 JavaScript/TypeScript AST"""
        for child in node.children:
            if child.type == 'function_declaration':
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'function',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'class_declaration':
                name_node = child.child_by_field_name('name')
                if name_node:
                    classes.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'class',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type in ['import_statement', 'export_statement']:
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'import',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_js_ast(child, functions, classes, imports)

    def _walk_go_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 Go AST"""
        for child in node.children:
            if child.type == 'function_declaration':
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'function',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'import_declaration':
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'import',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_go_ast(child, functions, classes, imports)

    def _walk_rust_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 Rust AST"""
        for child in node.children:
            if child.type == 'function_item':
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'function',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'struct_item':
                name_node = child.child_by_field_name('name')
                if name_node:
                    classes.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'struct',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'use_declaration':
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'use',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_rust_ast(child, functions, classes, imports)

    def _walk_java_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 Java AST"""
        for child in node.children:
            if child.type == 'method_declaration':
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'method',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'class_declaration':
                name_node = child.child_by_field_name('name')
                if name_node:
                    classes.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'class',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'import_declaration':
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'import',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_java_ast(child, functions, classes, imports)

    def _walk_c_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """遍历 C/C++ AST"""
        for child in node.children:
            if child.type == 'function_definition':
                # C 函数名在 declarator 中
                declarator = child.child_by_field_name('declarator')
                if declarator:
                    name_node = declarator.child_by_field_name('declarator')
                    if name_node:
                        functions.append({
                            'name': name_node.text.decode('utf-8'),
                            'type': 'function',
                            'start_line': child.start_point[0] + 1,
                        })

            elif child.type == 'class_specifier':
                name_node = child.child_by_field_name('name')
                if name_node:
                    classes.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': 'class',
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type == 'preproc_include':
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': 'include',
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_c_ast(child, functions, classes, imports)

    def _walk_generic_ast(self, node: Any, functions: List, classes: List, imports: List) -> None:
        """通用 AST 遍历"""
        # 基于节点类型的通用匹配
        function_types = ['function_definition', 'function_declaration', 'method_declaration']
        class_types = ['class_definition', 'class_declaration', 'struct_item']
        import_types = ['import_statement', 'import_declaration', 'use_declaration']

        for child in node.children:
            if child.type in function_types:
                name_node = child.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': child.type,
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type in class_types:
                name_node = child.child_by_field_name('name')
                if name_node:
                    classes.append({
                        'name': name_node.text.decode('utf-8'),
                        'type': child.type,
                        'start_line': child.start_point[0] + 1,
                    })

            elif child.type in import_types:
                imports.append({
                    'statement': child.text.decode('utf-8'),
                    'type': child.type,
                    'start_line': child.start_point[0] + 1,
                })

            # 递归遍历
            self._walk_generic_ast(child, functions, classes, imports)

    def _parse_code_files(self, files: List[Path]) -> tuple:
        """批量解析代码文件"""
        all_functions = []
        all_classes = []
        all_imports = []

        for file_path in files:
            if not self.language_config.is_supported(file_path):
                continue

            result = self.parse_file(file_path)
            if 'error' not in result:
                all_functions.extend(result.get('functions', []))
                all_classes.extend(result.get('classes', []))
                all_imports.extend(result.get('imports', []))

        return all_functions, all_classes, all_imports

    def _detect_main_language(self, code_files: List[Path]) -> str:
        """检测主要语言"""
        if not code_files:
            return "未知"

        language_counts = {}
        for file_path in code_files:
            lang = self.language_config.detect_language(file_path)
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1

        if language_counts:
            return max(language_counts, key=language_counts.get)

        return "未知"

    def _detect_system_type(self, code_files: List[Path], project_path: Path) -> str:
        """检测系统类型"""
        pipeline_indicators = ['pipeline', 'flow', 'process', 'etl', 'batch', 'worker']
        api_indicators = ['api', 'route', 'controller', 'handler', 'endpoint', 'server']

        dirs = [d.name.lower() for d in project_path.iterdir()
                if d.is_dir() and not d.name.startswith('.')]

        has_pipeline = any(ind in d for d in dirs for ind in pipeline_indicators)
        has_api = any(ind in d for d in dirs for ind in api_indicators)

        if has_pipeline and has_api:
            return "混合系统"
        elif has_pipeline:
            return "数据处理系统"
        elif has_api:
            return "交互系统"

        return "未知"

    def _detect_modules(self, project_path: Path) -> List[str]:
        """检测模块"""
        modules = []

        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in self.IGNORE_DIRS:
                if (item / '__init__.py').exists():
                    modules.append(item.name)
                elif any(self.language_config.is_supported(f)
                        for f in item.iterdir() if f.is_file()):
                    modules.append(item.name)

        return modules

    def _find_entry_points(self, files: List[Path]) -> List[str]:
        """查找入口文件"""
        entry_points = []

        for file_path in files:
            lang = self.language_config.detect_language(file_path)
            if lang:
                config = self.language_config.get_config(lang)
                if config and file_path.name in config.get('entry_points', []):
                    entry_points.append(file_path.name)

        return entry_points

    def _calculate_stats(
        self,
        all_files: List[Path],
        code_files: List[Path],
        functions: List[Dict],
        classes: List[Dict]
    ) -> Dict:
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
            "functions": len(functions),
            "classes": len(classes)
        }