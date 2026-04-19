"""
KnowledgeForge CLI 入口

Phase 0 基础命令：
- forge: 解析项目
- query: 搜索知识
- list: 列出项目

Phase 2 新增命令：
- blast-radius: 影响范围分析
- verify: 测试验证
- install: MCP服务器安装
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

    # blast-radius 命令 (Phase 2)
    blast_parser = subparsers.add_parser('blast-radius', help='分析模式影响范围')
    blast_parser.add_argument('pattern_id', type=str, help='模式ID或名称')
    blast_parser.add_argument('--depth', type=int, default=3, help='分析深度（1-5）')
    blast_parser.add_argument('--project', type=str, help='项目过滤')

    # verify 命令 (Phase 2)
    verify_parser = subparsers.add_parser('verify', help='运行测试验证模式')
    verify_parser.add_argument('pattern_id', type=str, nargs='?', help='模式ID（可选，不指定则验证所有）')
    verify_parser.add_argument('--project-path', type=str, help='项目路径（用于运行测试）')
    verify_parser.add_argument('--test-command', type=str, help='自定义测试命令')

    # install 命令 (Phase 2)
    install_parser = subparsers.add_parser('install', help='安装MCP服务器')
    install_parser.add_argument('--mcp', action='store_true', help='安装为MCP服务器')
    install_parser.add_argument('--platform', type=str, default='claude', choices=['claude', 'cursor'], help='目标平台')
    install_parser.add_argument('--config-path', type=str, help='配置文件保存路径')

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
        elif args.command == 'blast-radius':
            return _handle_blast_radius(args)
        elif args.command == 'verify':
            return _handle_verify(args)
        elif args.command == 'install':
            return _handle_install(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1


def _handle_blast_radius(args) -> int:
    """处理 blast-radius 命令"""
    from knowledgeforge.analysis import get_blast_radius_analyzer

    analyzer = get_blast_radius_analyzer()

    print(f"分析模式影响范围: {args.pattern_id}")
    print(f"分析深度: {args.depth}")

    result = analyzer.analyze(
        pattern_id=args.pattern_id,
        depth=args.depth,
        project_filter=args.project
    )

    if 'error' in result:
        print(f"错误: {result['error']}")
        return 1

    print(f"\n模式: {result.get('pattern_name')}")
    print(f"置信度: {result.get('confidence')}")
    print(f"风险等级: {result.get('risk_level')}")

    # 显示影响模块
    modules = result.get('affected_modules', [])
    if modules:
        print(f"\n影响模块 ({len(modules)}):")
        for mod in modules:
            print(f"  - {mod.get('name')} (关系: {mod.get('relation')})")

    # 显示相关模式
    related = result.get('related_patterns', [])
    if related:
        print(f"\n相关模式 ({len(related)}):")
        for rp in related:
            print(f"  - {rp.get('pattern_name')} (相似度: {rp.get('similarity', 0):.2f})")

    # 显示调用链
    call_chain = result.get('call_chain', [])
    if call_chain:
        print(f"\n调用链 ({len(call_chain)}):")
        for cc in call_chain:
            print(f"  - {cc.get('type')}: {cc.get('name')}")

    print(f"\n修改建议: {result.get('modification_recommendation')}")

    return 0


def _handle_verify(args) -> int:
    """处理 verify 命令"""
    from knowledgeforge.verification import get_verify_runner

    runner = get_verify_runner()

    project_path = Path(args.project_path) if args.project_path else None

    if args.pattern_id:
        print(f"验证模式: {args.pattern_id}")

        if project_path:
            print(f"项目路径: {project_path}")

        result = runner.run_verify(
            pattern_id=args.pattern_id,
            project_path=project_path,
            test_command=args.test_command
        )

        if 'error' in result:
            print(f"错误: {result['error']}")
            return 1

        print(f"\n测试结果:")
        print(f"  发现测试: {result.get('tests_found')}")
        print(f"  执行测试: {result.get('tests_executed')}")
        print(f"  通过测试: {result.get('tests_passed')}")
        print(f"  成功率: {result.get('success_rate', 0):.2%}")

        print(f"\n置信度变化:")
        print(f"  验证前: {result.get('confidence_before')}")
        print(f"  验证后: {result.get('confidence_after')}")
        print(f"  是否提升: {'是' if result.get('promoted') else '否'}")

    else:
        if not project_path:
            print("错误: 验证所有模式需要指定 --project-path")
            return 1

        print(f"验证项目所有模式: {project_path}")
        result = runner.verify_all_patterns(project_path)

        print(f"\n验证结果:")
        print(f"  总模式数: {result.get('total_patterns')}")
        print(f"  置信度提升数: {result.get('promoted_count')}")

    return 0


def _handle_install(args) -> int:
    """处理 install 命令"""
    if args.mcp:
        from knowledgeforge.mcp import KnowledgeForgeMCPServer

        server = KnowledgeForgeMCPServer()

        if args.platform == 'claude':
            config_path = Path(args.config_path or "~/.claude/config.json")
            config_path = config_path.expanduser()

            config = server.generate_config(config_path)

            print(f"MCP服务器配置已生成")
            print(f"配置文件: {config_path}")
            print(f"\n配置内容:")
            print(f"  服务名: knowledgeforge")
            print(f"  命令: python -m knowledgeforge.mcp.server")

            print(f"\n重启 Claude Desktop 以加载配置")

        elif args.platform == 'cursor':
            config_path = Path(args.config_path or "~/.cursor/mcp.json")
            config_path = config_path.expanduser()

            config = server.generate_config(config_path)

            print(f"MCP服务器配置已生成")
            print(f"配置文件: {config_path}")
            print(f"\n重启 Cursor IDE 以加载配置")

        return 0

    print("使用 --mcp 参数安装为MCP服务器")
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