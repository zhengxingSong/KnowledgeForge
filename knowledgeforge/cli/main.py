"""
KnowledgeForge CLI 入口

提供 forge、query、list 等命令。
"""

import argparse
import sys
from pathlib import Path

from knowledgeforge.skeleton import KnowledgeForgePipeline


def main():
    """CLI入口函数"""
    parser = argparse.ArgumentParser(
        prog='knowledgeforge',
        description='开源项目知识锻造系统 - 从开源项目中提取设计模式和心智模型'
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # forge 命令
    forge_parser = subparsers.add_parser('forge', help='解析项目并锻造知识')
    forge_parser.add_argument(
        'project_path',
        type=str,
        help='项目根目录路径'
    )
    forge_parser.add_argument(
        '--mode',
        type=str,
        default='full',
        choices=['full', 'incremental'],
        help='解析模式：full（全量）或 incremental（增量）'
    )
    forge_parser.add_argument(
        '--output',
        type=str,
        default='knowledge_output',
        help='输出目录'
    )

    # query 命令
    query_parser = subparsers.add_parser('query', help='搜索知识')
    query_parser.add_argument('search_term', type=str, help='搜索关键词')
    query_parser.add_argument('--type', type=str, help='过滤类型（pattern/mental_model/project）')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出已解析的项目')
    list_parser.add_argument('--type', type=str, help='过滤类型（patterns/mental_models/projects）')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == 'forge':
            return _handle_forge(args)
        elif args.command == 'query':
            return _handle_query(args)
        elif args.command == 'list':
            return _handle_list(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1


def _handle_forge(args) -> int:
    """处理 forge 命令"""
    project_path = Path(args.project_path)

    if not project_path.exists():
        print(f"错误: 项目路径不存在 - {project_path}")
        return 1

    if not project_path.is_dir():
        print(f"错误: 项目路径不是目录 - {project_path}")
        return 1

    print(f"正在解析项目: {project_path}")
    print(f"解析模式: {args.mode}")

    # 创建Pipeline
    pipeline = KnowledgeForgePipeline()

    # 执行解析
    result = pipeline.forge(project_path, mode=args.mode)

    # 输出结果
    if result.success:
        print(f"\n解析成功!")
        print(f"  - 发现设计模式: {len(result.patterns)}")
        print(f"  - 发现心智模型: {len(result.mental_models)}")

        if result.patterns:
            print("\n设计模式列表:")
            for pattern in result.patterns:
                print(f"  [{pattern.get('id', '')}] {pattern.get('name', '')}")

        if result.mental_models:
            print("\n心智模型列表:")
            for model in result.mental_models:
                print(f"  [{model.get('id', '')}] {model.get('name', '')}")

        print(f"\n输出目录: {args.output}")
        return 0
    else:
        print(f"\n解析失败!")
        for error in result.errors:
            print(f"  - [{error.get('phase', '')}] {error.get('error', '')}")
        return 1


def _handle_query(args) -> int:
    """处理 query 命令"""
    from knowledgeforge.defaults import JSONIndexer

    indexer = JSONIndexer()

    filters = {}
    if args.type:
        filters['type'] = args.type

    results = indexer.search(args.search_term, filters)

    if not results:
        print(f"未找到匹配 '{args.search_term}' 的结果")
        return 0

    print(f"找到 {len(results)} 个结果:\n")
    for result in results:
        type_name = result.get('type', '')
        name = result.get('name', '')
        if type_name == 'pattern':
            print(f"  [模式] {name} (ID: {result.get('id', '')})")
        elif type_name == 'mental_model':
            print(f"  [心智模型] {name} (ID: {result.get('id', '')})")
        elif type_name == 'project':
            print(f"  [项目] {name} ({result.get('patterns_count', 0)} 模式, {result.get('mental_models_count', 0)} 心智模型)")

    return 0


def _handle_list(args) -> int:
    """处理 list 命令"""
    import json
    from knowledgeforge.defaults import JSONIndexer

    indexer = JSONIndexer()

    # 加载索引
    index = indexer._load_index()

    if args.type == 'patterns':
        patterns = index.get('patterns', {})
        print(f"设计模式 ({len(patterns)}):\n")
        for pattern_id, pattern in patterns.items():
            print(f"  [{pattern_id}] {pattern.get('name', '')} (来自: {pattern.get('source_project', '')})")

    elif args.type == 'mental_models':
        models = index.get('mental_models', {})
        print(f"心智模型 ({len(models)}):\n")
        for model_id, model in models.items():
            print(f"  [{model_id}] {model.get('name', '')} (来自: {model.get('source_project', '')})")

    elif args.type == 'projects':
        projects = index.get('projects', {})
        print(f"已解析项目 ({len(projects)}):\n")
        for project_name, project in projects.items():
            print(f"  {project_name}")
            print(f"    - 类型: {project.get('type', '')}")
            print(f"    - 语言: {project.get('language', '')}")
            print(f"    - 模式数: {project.get('patterns_count', 0)}")
            print(f"    - 心智模型数: {project.get('mental_models_count', 0)}")
            print()

    else:
        # 显示所有
        stats = index.get('stats', {})
        print(f"知识库统计:\n")
        print(f"  项目总数: {stats.get('total_projects', 0)}")
        print(f"  设计模式总数: {stats.get('total_patterns', 0)}")
        print(f"  心智模型总数: {stats.get('total_mental_models', 0)}")
        print(f"  最后更新: {stats.get('last_update', '')}")

    return 0


if __name__ == '__main__':
    sys.exit(main())