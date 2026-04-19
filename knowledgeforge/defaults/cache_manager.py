"""
CacheManager - 缓存管理模块

基于 SHA256 的文件变更检测，支持增量解析。
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from knowledgeforge.skeleton.result import ForgeResult


class CacheManager:
    """
    缓存管理器

    功能：
    - 计算文件 SHA256
    - 检测文件变更
    - 管理 manifest.json
    - 缓存解析结果
    """

    # Manifest 文件名
    MANIFEST_FILENAME = ".knowledgeforge_manifest.json"

    # 缓存目录
    CACHE_DIR = ".knowledgeforge"

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录，默认为项目根目录下的 .knowledgeforge
        """
        self.cache_dir = cache_dir

    def compute_sha256(self, file_path: Path) -> str:
        """
        计算文件 SHA256

        Args:
            file_path: 文件路径

        Returns:
            str: SHA256 哈希值
        """
        try:
            with open(file_path, 'rb') as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()
            return sha256_hash
        except Exception:
            return ""

    def load_manifest(self, project_path: Path) -> Dict:
        """
        加载 manifest.json

        Args:
            project_path: 项目根目录

        Returns:
            Dict: Manifest 数据，不存在返回空 dict
        """
        manifest_path = project_path / self.MANIFEST_FILENAME

        if not manifest_path.exists():
            return {}

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_manifest(self, project_path: Path, manifest: Dict) -> bool:
        """
        保存 manifest.json

        Args:
            project_path: 项目根目录
            manifest: Manifest 数据

        Returns:
            bool: 成功返回 True
        """
        manifest_path = project_path / self.MANIFEST_FILENAME

        try:
            # 确保 manifest 包含必要字段
            if 'files' not in manifest:
                manifest['files'] = {}
            if 'version' not in manifest:
                manifest['version'] = '1.0'
            if 'last_parse' not in manifest:
                manifest['last_parse'] = None

            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def is_changed(self, file_path: Path, manifest: Dict) -> bool:
        """
        检查文件是否变更

        Args:
            file_path: 文件路径
            manifest: Manifest 数据

        Returns:
            bool: 变更返回 True，未变更返回 False
        """
        relative_path = str(file_path)
        current_hash = self.compute_sha256(file_path)

        # 文件不在 manifest 中，视为变更
        if 'files' not in manifest:
            return True

        if relative_path not in manifest['files']:
            return True

        # SHA256 不同，视为变更
        cached_hash = manifest['files'].get(relative_path, {}).get('sha256', '')
        return current_hash != cached_hash

    def detect_changes(self, project_path: Path, files: List[Path]) -> List[Path]:
        """
        检测所有变更文件

        Args:
            project_path: 项目根目录
            files: 文件列表

        Returns:
            List[Path]: 变更文件列表
        """
        manifest = self.load_manifest(project_path)
        changed_files = []

        for file_path in files:
            if self.is_changed(file_path, manifest):
                changed_files.append(file_path)

        return changed_files

    def update_file_hash(self, manifest: Dict, file_path: Path) -> Dict:
        """
        更新文件哈希

        Args:
            manifest: Manifest 数据
            file_path: 文件路径

        Returns:
            Dict: 更新后的 manifest
        """
        relative_path = str(file_path)
        sha256 = self.compute_sha256(file_path)

        if 'files' not in manifest:
            manifest['files'] = {}

        manifest['files'][relative_path] = {
            'sha256': sha256,
            'last_modified': file_path.stat().st_mtime if file_path.exists() else 0
        }

        return manifest

    def save_result(self, project_path: Path, result: ForgeResult) -> bool:
        """
        缓存解析结果

        Args:
            project_path: 项目根目录
            result: 解析结果

        Returns:
            bool: 成功返回 True
        """
        cache_path = self._get_cache_path(project_path)

        try:
            # 创建缓存目录
            cache_path.mkdir(parents=True, exist_ok=True)

            # 保存结果
            result_file = cache_path / "result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    def load_result(self, project_path: Path) -> Optional[ForgeResult]:
        """
        加载缓存结果

        Args:
            project_path: 项目根目录

        Returns:
            Optional[ForgeResult]: 缓存结果，不存在返回 None
        """
        cache_path = self._get_cache_path(project_path)
        result_file = cache_path / "result.json"

        if not result_file.exists():
            return None

        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return ForgeResult(
                project=data.get('project'),
                patterns=data.get('patterns', []),
                mental_models=data.get('mental_models', []),
                tech_knowledge=data.get('tech_knowledge', []),
                success=data.get('success', False),
                errors=data.get('errors', []),
                parse_metadata=data.get('parse_metadata', {})
            )
        except Exception:
            return None

    def clear_cache(self, project_path: Path) -> bool:
        """
        清除缓存

        Args:
            project_path: 项目根目录

        Returns:
            bool: 成功返回 True
        """
        cache_path = self._get_cache_path(project_path)

        if not cache_path.exists():
            return True

        try:
            # 删除缓存目录内容
            for file in cache_path.iterdir():
                file.unlink()

            # 删除 manifest
            manifest_path = project_path / self.MANIFEST_FILENAME
            if manifest_path.exists():
                manifest_path.unlink()

            return True
        except Exception:
            return False

    def get_cache_stats(self, project_path: Path) -> Dict:
        """
        获取缓存统计

        Args:
            project_path: 项目根目录

        Returns:
            Dict: 缓存统计信息
        """
        manifest = self.load_manifest(project_path)

        return {
            'cached_files': len(manifest.get('files', {})),
            'last_parse': manifest.get('last_parse'),
            'version': manifest.get('version'),
            'cache_size': self._calculate_cache_size(project_path)
        }

    def _get_cache_path(self, project_path: Path) -> Path:
        """获取缓存目录路径"""
        if self.cache_dir:
            return self.cache_dir
        return project_path / self.CACHE_DIR

    def _calculate_cache_size(self, project_path: Path) -> int:
        """计算缓存大小"""
        cache_path = self._get_cache_path(project_path)

        if not cache_path.exists():
            return 0

        total_size = 0
        for file in cache_path.iterdir():
            if file.is_file():
                total_size += file.stat().st_size

        return total_size


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager