"""
LanguageConfig - 语言配置模块

支持 23+ 编程语言的配置，包括：
- 文件后缀映射
- tree-sitter 语言包映射
- 解析器加载策略
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

from knowledgeforge.skeleton.confidence import ExtractionConfidence


class LanguageConfig:
    """
    语言配置类

    支持 23+ 编程语言的统一配置。
    """

    # 支持的语言配置
    SUPPORTED_LANGUAGES: Dict[str, Dict] = {
        # Python 系列
        'python': {
            'extensions': ['.py', '.pyw', '.pyi'],
            'tree_sitter_lang': 'python',
            'aliases': ['py'],
            'comment_style': '#',
            'entry_points': ['main.py', 'app.py', '__main__.py'],
        },

        # JavaScript 系列
        'javascript': {
            'extensions': ['.js', '.mjs', '.cjs'],
            'tree_sitter_lang': 'javascript',
            'aliases': ['js', 'node'],
            'comment_style': '//',
            'entry_points': ['index.js', 'app.js', 'main.js'],
        },

        # TypeScript 系列
        'typescript': {
            'extensions': ['.ts'],
            'tree_sitter_lang': 'typescript',
            'aliases': ['ts'],
            'comment_style': '//',
            'entry_points': ['index.ts', 'app.ts', 'main.ts'],
        },

        # TypeScript JSX
        'tsx': {
            'extensions': ['.tsx'],
            'tree_sitter_lang': 'tsx',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['index.tsx', 'app.tsx'],
        },

        # JavaScript JSX
        'jsx': {
            'extensions': ['.jsx'],
            'tree_sitter_lang': 'jsx',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['index.jsx', 'app.jsx'],
        },

        # Go
        'go': {
            'extensions': ['.go'],
            'tree_sitter_lang': 'go',
            'aliases': ['golang'],
            'comment_style': '//',
            'entry_points': ['main.go'],
        },

        # Rust
        'rust': {
            'extensions': ['.rs'],
            'tree_sitter_lang': 'rust',
            'aliases': ['rs'],
            'comment_style': '//',
            'entry_points': ['main.rs', 'lib.rs'],
        },

        # Java
        'java': {
            'extensions': ['.java'],
            'tree_sitter_lang': 'java',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['Main.java', 'App.java'],
        },

        # Kotlin
        'kotlin': {
            'extensions': ['.kt', '.kts'],
            'tree_sitter_lang': 'kotlin',
            'aliases': ['kt'],
            'comment_style': '//',
            'entry_points': ['Main.kt', 'App.kt'],
        },

        # C
        'c': {
            'extensions': ['.c', '.h'],
            'tree_sitter_lang': 'c',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['main.c'],
        },

        # C++
        'cpp': {
            'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.hxx'],
            'tree_sitter_lang': 'cpp',
            'aliases': ['c++', 'cxx'],
            'comment_style': '//',
            'entry_points': ['main.cpp'],
        },

        # Ruby
        'ruby': {
            'extensions': ['.rb', '.rake'],
            'tree_sitter_lang': 'ruby',
            'aliases': ['rb'],
            'comment_style': '#',
            'entry_points': ['main.rb', 'app.rb'],
        },

        # PHP
        'php': {
            'extensions': ['.php', '.phtml'],
            'tree_sitter_lang': 'php',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['index.php', 'app.php'],
        },

        # Swift
        'swift': {
            'extensions': ['.swift'],
            'tree_sitter_lang': 'swift',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['main.swift', 'App.swift'],
        },

        # Scala
        'scala': {
            'extensions': ['.scala', '.sc'],
            'tree_sitter_lang': 'scala',
            'aliases': [],
            'comment_style': '//',
            'entry_points': ['Main.scala', 'App.scala'],
        },

        # Lua
        'lua': {
            'extensions': ['.lua'],
            'tree_sitter_lang': 'lua',
            'aliases': [],
            'comment_style': '--',
            'entry_points': ['main.lua', 'init.lua'],
        },

        # R
        'r': {
            'extensions': ['.r', '.R', '.rscript'],
            'tree_sitter_lang': 'r',
            'aliases': ['R'],
            'comment_style': '#',
            'entry_points': ['main.R'],
        },

        # Shell
        'bash': {
            'extensions': ['.sh', '.bash'],
            'tree_sitter_lang': 'bash',
            'aliases': ['shell', 'sh'],
            'comment_style': '#',
            'entry_points': [],
        },

        # JSON
        'json': {
            'extensions': ['.json', '.jsonc'],
            'tree_sitter_lang': 'json',
            'aliases': [],
            'comment_style': None,
            'entry_points': [],
        },

        # YAML
        'yaml': {
            'extensions': ['.yaml', '.yml'],
            'tree_sitter_lang': 'yaml',
            'aliases': [],
            'comment_style': '#',
            'entry_points': [],
        },

        # TOML
        'toml': {
            'extensions': ['.toml'],
            'tree_sitter_lang': 'toml',
            'aliases': [],
            'comment_style': '#',
            'entry_points': [],
        },

        # HTML
        'html': {
            'extensions': ['.html', '.htm'],
            'tree_sitter_lang': 'html',
            'aliases': [],
            'comment_style': None,
            'entry_points': ['index.html'],
        },

        # CSS
        'css': {
            'extensions': ['.css', '.scss', '.sass', '.less'],
            'tree_sitter_lang': 'css',
            'aliases': [],
            'comment_style': None,
            'entry_points': [],
        },

        # Markdown
        'markdown': {
            'extensions': ['.md', '.markdown'],
            'tree_sitter_lang': 'markdown',
            'aliases': ['md'],
            'comment_style': None,
            'entry_points': [],
        },
    }

    # 扩展名到语言的映射（缓存）
    _extension_map: Dict[str, str] = {}

    def __init__(self):
        """初始化语言配置"""
        self._build_extension_map()

    def _build_extension_map(self) -> None:
        """构建扩展名映射"""
        if self._extension_map:
            return

        for lang, config in self.SUPPORTED_LANGUAGES.items():
            for ext in config['extensions']:
                self._extension_map[ext.lower()] = lang

    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        检测文件语言

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 语言名称，未知返回 None
        """
        ext = file_path.suffix.lower()
        return self._extension_map.get(ext)

    def get_config(self, language: str) -> Optional[Dict]:
        """
        获取语言配置

        Args:
            language: 语言名称

        Returns:
            Optional[Dict]: 语言配置，不存在返回 None
        """
        # 检查直接匹配
        if language in self.SUPPORTED_LANGUAGES:
            return self.SUPPORTED_LANGUAGES[language]

        # 检查别名
        for lang, config in self.SUPPORTED_LANGUAGES.items():
            if language.lower() in config.get('aliases', []):
                return config

        return None

    def get_tree_sitter_lang(self, language: str) -> Optional[str]:
        """
        获取 tree-sitter 语言名称

        Args:
            language: 语言名称

        Returns:
            Optional[str]: tree-sitter 语言名称
        """
        config = self.get_config(language)
        if config:
            return config.get('tree_sitter_lang')
        return None

    def get_extensions(self, language: str) -> List[str]:
        """
        获取语言文件扩展名

        Args:
            language: 语言名称

        Returns:
            List[str]: 扩展名列表
        """
        config = self.get_config(language)
        if config:
            return config.get('extensions', [])
        return []

    def is_supported(self, file_path: Path) -> bool:
        """
        检查文件是否支持解析

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否支持
        """
        return self.detect_language(file_path) is not None

    def get_supported_languages(self) -> Set[str]:
        """
        获取所有支持的语言名称

        Returns:
            Set[str]: 语言名称集合
        """
        return set(self.SUPPORTED_LANGUAGES.keys())

    def get_supported_extensions(self) -> Set[str]:
        """
        获取所有支持的文件扩展名

        Returns:
            Set[str]: 扩展名集合
        """
        return set(self._extension_map.keys())


# 全局配置实例
_global_config: Optional[LanguageConfig] = None


def get_language_config() -> LanguageConfig:
    """获取全局语言配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = LanguageConfig()
    return _global_config