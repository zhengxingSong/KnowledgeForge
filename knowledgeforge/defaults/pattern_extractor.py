"""
DefaultPatternExtractor - 默认设计模式提取器

基于规则检测常见设计模式（Phase 0 基础版）。
"""

from typing import Dict, List

from knowledgeforge.skeleton.contracts import PatternExtractorContract


class DefaultPatternExtractor(PatternExtractorContract):
    """
    默认设计模式提取器

    Phase 0 基础版本：
    - 基于目录结构检测模式
    - 基于命名特征检测模式
    - 无深度代码分析

    输出置信度：INFERRED_PATTERN
    """

    def extract_patterns(self, structure: Dict) -> List[Dict]:
        """
        提取设计模式

        Args:
            structure: 项目结构信息（Parser输出）

        Returns:
            List[Dict]: 设计模式列表
        """
        patterns = []

        try:
            if structure is None:
                return []

            # 检测流水线骨架模式
            if self._detect_pipeline_pattern(structure):
                patterns.append(self._create_pipeline_pattern(structure))

            # 检测契约驱动模式
            if self._detect_contract_pattern(structure):
                patterns.append(self._create_contract_pattern(structure))

            # 检测模块独立性模式
            if self._detect_module_independence(structure):
                patterns.append(self._create_module_pattern(structure))

            # 检测配置驱动模式
            if self._detect_config_driven(structure):
                patterns.append(self._create_config_pattern(structure))

            # 检测分层架构模式
            if self._detect_layered_architecture(structure):
                patterns.append(self._create_layered_pattern(structure))

            # 分配ID
            for i, pattern in enumerate(patterns):
                pattern["id"] = f"P-{i+1:03d}"

        except Exception as e:
            print(f"[DefaultPatternExtractor] 处理异常: {e}")
            return []

        return patterns

    def _detect_pipeline_pattern(self, structure: Dict) -> bool:
        """检测流水线模式"""
        modules = structure.get("structure", {}).get("modules", [])
        pipeline_names = ['pipeline', 'flow', 'process', 'workflow', 'chain', 'etl']

        # 检查模块名
        if any(name.lower() in pipeline_names for name in modules):
            return True

        # 检查系统类型
        if structure.get("type") == "数据处理系统":
            return True

        return False

    def _detect_contract_pattern(self, structure: Dict) -> bool:
        """检测契约驱动模式"""
        modules = structure.get("structure", {}).get("modules", [])
        contract_names = ['contract', 'interface', 'base', 'abstract', 'protocol', 'skeleton']

        return any(name.lower() in contract_names for name in modules)

    def _detect_module_independence(self, structure: Dict) -> bool:
        """检测模块独立性"""
        modules = structure.get("structure", {}).get("modules", [])
        # 至少有3个模块，且模块名不包含紧耦合关键词
        tight_coupling = ['util', 'helper', 'common']

        if len(modules) >= 3:
            # 检查是否大多数模块不是紧耦合的
            non_tight = [m for m in modules if not any(tc in m.lower() for tc in tight_coupling)]
            return len(non_tight) >= 2

        return False

    def _detect_config_driven(self, structure: Dict) -> bool:
        """检测配置驱动模式"""
        config_files = structure.get("structure", {}).get("config_files", [])

        # 有多个配置文件
        return len(config_files) >= 2

    def _detect_layered_architecture(self, structure: Dict) -> bool:
        """检测分层架构模式"""
        modules = structure.get("structure", {}).get("modules", [])

        # 常见的分层名称
        layer_names = {
            'api', 'controller', 'handler',  # 表现层
            'service', 'business', 'logic',  # 业务层
            'data', 'dao', 'repository', 'model', 'storage', 'db',  # 数据层
            'core', 'domain', 'entity'       # 核心层
        }

        found_layers = set()
        for module in modules:
            module_lower = module.lower()
            for layer_name in layer_names:
                if layer_name in module_lower:
                    found_layers.add(layer_name)

        # 至少发现2个不同层
        return len(found_layers) >= 2

    def _create_pipeline_pattern(self, structure: Dict) -> Dict:
        """创建流水线模式"""
        return {
            "id": "",
            "name": "流水线骨架模式",
            "description": "数据处理系统的单向流水线骨架，各阶段顺序执行",
            "applicable_scenarios": [
                "数据处理系统",
                "ETL流程",
                "批处理任务",
                "数据转换流水线"
            ],
            "not_applicable_scenarios": [
                "交互式系统",
                "实时响应系统",
                "需要频繁回溯的系统"
            ],
            "code_template": self._get_pipeline_template(),
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "检测到pipeline/flow/process相关模块名或系统类型为数据处理系统",
                "structural_match": True,
                "naming_hints": ["pipeline", "flow", "process"]
            }
        }

    def _create_contract_pattern(self, structure: Dict) -> Dict:
        """创建契约驱动模式"""
        return {
            "id": "",
            "name": "契约驱动模式",
            "description": "所有实现返回相同格式，可拔插替换，骨架只依赖契约",
            "applicable_scenarios": [
                "多实现可替换",
                "拔插架构",
                "扩展点设计",
                "插件系统"
            ],
            "not_applicable_scenarios": [
                "单一实现",
                "紧密耦合",
                "不需要扩展的系统"
            ],
            "code_template": self._get_contract_template(),
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "检测到contract/interface/base相关模块名",
                "structural_match": True,
                "naming_hints": ["contract", "interface", "abstract"]
            }
        }

    def _create_module_pattern(self, structure: Dict) -> Dict:
        """创建模块独立性模式"""
        return {
            "id": "",
            "name": "模块独立性模式",
            "description": "模块通过接口通信，职责边界清晰，降低耦合度",
            "applicable_scenarios": [
                "多模块系统",
                "大型项目",
                "需要并行开发的系统",
                "团队协作开发"
            ],
            "not_applicable_scenarios": [
                "紧密耦合系统",
                "单文件项目",
                "小型原型项目"
            ],
            "code_template": self._get_module_template(),
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": f"检测到{len(structure.get('structure', {}).get('modules', []))}个独立模块",
                "structural_match": True
            }
        }

    def _create_config_pattern(self, structure: Dict) -> Dict:
        """创建配置驱动模式"""
        return {
            "id": "",
            "name": "配置驱动模式",
            "description": "系统行为由配置文件控制，便于环境切换和参数调整",
            "applicable_scenarios": [
                "多环境部署",
                "参数化系统",
                "需要灵活配置的系统"
            ],
            "not_applicable_scenarios": [
                "硬编码系统",
                "配置固定的系统"
            ],
            "code_template": self._get_config_template(),
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "检测到多个配置文件",
                "structural_match": True
            }
        }

    def _create_layered_pattern(self, structure: Dict) -> Dict:
        """创建分层架构模式"""
        return {
            "id": "",
            "name": "分层架构模式",
            "description": "系统按职责分为表现层、业务层、数据层等，各层独立",
            "applicable_scenarios": [
                "企业应用",
                "需要关注点分离的系统",
                "大型业务系统"
            ],
            "not_applicable_scenarios": [
                "简单脚本",
                "单一职责工具"
            ],
            "code_template": self._get_layered_template(),
            "source_file": structure.get("name", "unknown"),
            "confidence": "inferred_pattern",
            "evidence": {
                "confidence": "inferred_pattern",
                "reasoning": "检测到分层目录结构（api/service/data等）",
                "structural_match": True
            }
        }

    def _get_pipeline_template(self) -> str:
        return '''
class Pipeline:
    """流水线骨架"""

    def __init__(self, steps: List[Step]):
        self.steps = steps

    def run(self, input_data: Any) -> Any:
        """执行流水线"""
        data = input_data
        for step in self.steps:
            data = step.process(data)
        return data
'''

    def _get_contract_template(self) -> str:
        return '''
class Contract(ABC):
    """扩展点契约"""

    @abstractmethod
    def execute(self, input: Input) -> Output:
        """执行方法，所有实现返回相同格式"""
        pass
'''

    def _get_module_template(self) -> str:
        return '''
class Module:
    """独立模块"""

    def __init__(self, dependency: Contract):
        """通过契约依赖，可替换实现"""
        self.dependency = dependency

    def process(self, data: Any) -> Any:
        """模块处理"""
        return self.dependency.execute(data)
'''

    def _get_config_template(self) -> str:
        return '''
class ConfigLoader:
    """配置加载器"""

    def load(self, config_path: str) -> Dict:
        """加载配置"""
        with open(config_path) as f:
            return yaml.safe_load(f)

class App:
    """应用入口"""

    def __init__(self, config: Dict):
        self.config = config

    def run(self):
        # 配置驱动行为
        pass
'''

    def _get_layered_template(self) -> str:
        return '''
# 表现层
class Controller:
    def handle_request(self, request):
        return self.service.process(request)

# 业务层
class Service:
    def process(self, data):
        result = self.repository.save(data)
        return result

# 数据层
class Repository:
    def save(self, data):
        # 存储数据
        pass
'''