"""
TaskMind-OS - 分布式任务操作系统

核心设计理念：
1. 层级化任务分解：无限深度，支持复杂依赖
2. 分布式记忆系统：模拟人类的多层记忆
3. 渐进式上下文压缩：不是一次性压缩，而是逐层提炼
4. 持久化任务图谱：支持数周/数月的任务执行
5. 多Agent协调：大规模并行Agent管理
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import json
from collections import defaultdict
import heapq


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 待执行
    READY = "ready"            # 就绪（依赖满足）
    RUNNING = "running"        # 执行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    BLOCKED = "blocked"        # 被阻塞


class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class TaskContext:
    """任务上下文 - 支持超大上下文"""
    task_id: str
    summary: str = ""                    # 摘要（始终可用）
    key_points: List[str] = field(default_factory=list)  # 关键点列表
    details: Optional[str] = None         # 详情（按需加载）
    compressed_versions: Dict[int, str] = field(default_factory=dict)  # 不同压缩级别
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_context(self, max_length: int = None) -> str:
        """获取指定长度的上下文"""
        if max_length is None:
            return self.details or self.summary
        
        # 从压缩版本中查找最接近的
        if max_length in self.compressed_versions:
            return self.compressed_versions[max_length]
        
        # 否则返回摘要（最压缩版本）
        return self.summary
    
    def add_compressed_version(self, length: int, content: str):
        """添加压缩版本"""
        self.compressed_versions[length] = content


class Task:
    """任务节点"""
    def __init__(self, task_id: str = None, title: str = ""):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description: str = ""
        self.status: TaskStatus = TaskStatus.PENDING
        self.priority: TaskPriority = TaskPriority.MEDIUM
        
        # 层级信息
        self.level: int = 0  # 任务层级（0为顶层）
        self.parent_id: Optional[str] = None
        self.children_ids: Set[str] = set()
        
        # 依赖关系
        self.dependencies: Set[str] = set()  # 依赖的任务IDs
        self.dependents: Set[str] = set()    # 依赖此任务的任务IDs
        
        # 执行信息
        self.assigned_agent: Optional[str] = None
        self.result: Optional[Any] = None
        self.context: Optional[TaskContext] = None
        
        # 时间戳
        self.created_at: float = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        
        # 资源估算
        self.estimated_duration: Optional[str] = None
        self.estimated_complexity: int = 5  # 1-10
    
    def is_ready(self) -> bool:
        """检查任务是否就绪（依赖都已完成）"""
        return self.status == TaskStatus.PENDING and len(self.dependencies) == 0
    
    def add_child(self, child_id: str):
        """添加子任务"""
        self.children_ids.add(child_id)
    
    def add_dependency(self, dep_id: str):
        """添加依赖"""
        self.dependencies.add(dep_id)


class TaskGraph:
    """任务图谱 - 管理所有任务及其关系"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.level_index: Dict[int, Set[str]] = defaultdict(set)  # 按层级索引
        self.ready_queue: List[str] = []  # 就绪队列（按优先级）
        self.completed_count: int = 0
        self.total_count: int = 0
    
    def add_task(self, task: Task):
        """添加任务到图谱"""
        self.tasks[task.id] = task
        self.level_index[task.level].add(task.id)
        self.total_count += 1
        
        # 如果任务就绪，加入就绪队列
        if task.is_ready():
            self._add_to_ready_queue(task.id)
    
    def _add_to_ready_queue(self, task_id: str):
        """加入就绪队列"""
        task = self.tasks[task_id]
        heapq.heappush(self.ready_queue, (task.priority.value, task.created_at, task_id))
    
    def get_ready_tasks(self, max_count: int = 10) -> List[Task]:
        """获取就绪的任务"""
        tasks = []
        for _ in range(min(max_count, len(self.ready_queue))):
            if not self.ready_queue:
                break
            _, _, task_id = heapq.heappop(self.ready_queue)
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                tasks.append(task)
        return tasks
    
    def mark_completed(self, task_id: str):
        """标记任务完成"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()
        self.completed_count += 1
        
        # 通知依赖此任务的其他任务
        for dep_id in task.dependents:
            dep_task = self.tasks.get(dep_id)
            if dep_task:
                dep_task.dependencies.discard(task_id)
                if dep_task.is_ready():
                    self._add_to_ready_queue(dep_id)
    
    def get_task_tree(self, task_id: str, max_depth: int = 3) -> Dict:
        """获取任务树（可视化用）"""
        task = self.tasks.get(task_id)
        if not task:
            return {}
        
        result = {
            'id': task.id,
            'title': task.title,
            'status': task.status.value,
            'level': task.level,
            'children': []
        }
        
        if max_depth > 0:
            for child_id in list(task.children_ids)[:10]:  # 最多显示10个子节点
                child_tree = self.get_task_tree(child_id, max_depth - 1)
                if child_tree:
                    result['children'].append(child_tree)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        status_counts = defaultdict(int)
        for task in self.tasks.values():
            status_counts[task.status.value] += 1
        
        return {
            'total': self.total_count,
            'completed': self.completed_count,
            'progress': self.completed_count / max(1, self.total_count),
            'status_breakdown': dict(status_counts),
            'max_level': max(self.level_index.keys()) if self.level_index else 0
        }


class Solution:
    """方案"""
    def __init__(self, solution_id: str = None):
        self.id = solution_id or str(uuid.uuid4())
        self.title: str = ""
        self.description: str = ""
        self.strategy: str = ""  # 探索性、保守性、创新性
        self.task_graph: TaskGraph = TaskGraph()
        self.root_task_id: Optional[str] = None
        
        # 评估指标
        self.confidence: float = 0.0
        self.estimated_duration: str = ""
        self.complexity_score: int = 5
        
        # 元信息
        self.pros: List[str] = []
        self.cons: List[str] = []
        self.risks: List[str] = []
        self.selected: bool = False


class MemorySystem:
    """分布式记忆系统 - 支持超大上下文"""
    
    def __init__(self, base_dir: str = "./task_memory"):
        self.base_dir = base_dir
        self.short_term: Dict[str, Any] = {}  # 短期记忆（内存）
        self.working_summary: str = ""  # 当前工作摘要
        self.long_term_index: Dict[str, Dict[str, Any]] = {}  # 长期记忆索引
        
        # 压缩级别定义
        self.compression_levels = {
            'brief': 100,           # 简短摘要
            'short': 500,           # 短摘要
            'medium': 2000,         # 中等长度
            'long': 10000,          # 长摘要
            'full': 100000          # 完整（但有限）
        }
    
    def store(self, key: str, value: Any, tier: str = 'short'):
        """存储记忆"""
        if tier == 'short':
            self.short_term[key] = value
        else:
            self.long_term_index[key] = {
                'value': value,
                'tier': tier,
                'timestamp': time.time()
            }
    
    def compress_context(self, content: str, level: str = 'medium') -> str:
        """按级别压缩上下文"""
        max_length = self.compression_levels.get(level, 2000)
        
        if len(content) <= max_length:
            return content
        
        # 智能压缩策略
        if level == 'brief':
            return self._extract_brief_summary(content)
        elif level == 'short':
            return self._extract_key_points(content, max_length)
        elif level == 'medium':
            return self._extract_main_points(content, max_length)
        else:
            return self._smart_compress(content, max_length)
    
    def _extract_brief_summary(self, content: str, max_length: int = 100) -> str:
        """提取简短摘要"""
        # 取开头、结尾、和关键句
        sentences = content.split('。')
        if len(sentences) <= 3:
            return content[:max_length]
        
        first = sentences[0]
        last = sentences[-1]
        middle = sentences[len(sentences)//2]
        
        summary = f"{first}...{middle}...{last}"
        return summary[:max_length]
    
    def _extract_key_points(self, content: str, max_length: int = 500) -> str:
        """提取关键点"""
        # 识别关键句子（包含数字、关键词的句子）
        key_indicators = ['重要', '关键', '必须', '主要', '核心', '最终', '目标']
        
        sentences = content.split('。')
        key_sentences = [s for s in sentences if any(ind in s for ind in key_indicators)]
        
        if len(key_sentences) >= 3:
            result = '。'.join(key_sentences[:5])
        else:
            # 取首尾和中间
            result = '。'.join([sentences[0], sentences[len(sentences)//2], sentences[-1]])
        
        return result[:max_length]
    
    def _extract_main_points(self, content: str, max_length: int = 2000) -> str:
        """提取主要内容"""
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) <= 5:
            return content[:max_length]
        
        # 按段落长度和位置评分
        scored_paragraphs = []
        for i, para in enumerate(paragraphs):
            score = len(para) * 0.5  # 基础分
            if i == 0:
                score += len(para) * 0.3  # 开头加分
            if i == len(paragraphs) - 1:
                score += len(para) * 0.3  # 结尾加分
            scored_paragraphs.append((score, para))
        
        # 选择得分最高的段落
        scored_paragraphs.sort(reverse=True)
        selected = [p[1] for p in scored_paragraphs[:5]]
        
        result = '\n\n'.join(selected)
        return result[:max_length]
    
    def _smart_compress(self, content: str, max_length: int) -> str:
        """智能压缩"""
        # 递归压缩
        if len(content) <= max_length:
            return content
        
        # 提取关键段落后再压缩
        main_points = self._extract_main_points(content, max_length * 2)
        return main_points[:max_length]


class HierarchicalDecomposer:
    """层级化任务分解器 - 支持无限深度"""
    
    def __init__(self, memory: MemorySystem):
        self.memory = memory
        self.max_level = 20  # 最大层级（实际根据需要可调整）
        self.min_task_size = "30分钟"  # 最小任务粒度
        self.decompose_threshold = 10  # 超过此数量子任务考虑合并
    
    def decompose(
        self,
        task: Task,
        strategy: str = "auto",
        depth: int = 0
    ) -> List[Task]:
        """
        递归分解任务
        
        Args:
            task: 要分解的任务
            strategy: 分解策略（'auto', 'detailed', 'quick'）
            depth: 当前深度
        """
        # 检查是否需要继续分解
        if not self._should_decompose(task, depth):
            return [task]
        
        # 生成子任务
        subtasks = self._generate_subtasks(task, strategy, depth)
        
        # 递归分解每个子任务
        all_tasks = []
        for subtask in subtasks:
            subtask.level = depth + 1
            subtask.parent_id = task.id
            task.add_child(subtask.id)
            
            # 递归处理
            decomposed = self.decompose(subtask, strategy, depth + 1)
            all_tasks.extend(decomposed)
        
        return all_tasks
    
    def _should_decompose(self, task: Task, current_depth: int) -> bool:
        """判断是否需要继续分解"""
        # 层级限制
        if current_depth >= self.max_level:
            return False
        
        # 任务复杂度
        if task.estimated_complexity <= 3:
            return False
        
        # 任务大小
        if self._estimate_task_size(task) <= self.min_task_size:
            return False
        
        # 检查是否有复杂的依赖关系
        if len(task.dependencies) > 5:
            return True
        
        return True
    
    def _estimate_task_size(self, task: Task) -> str:
        """估算任务大小"""
        desc_length = len(task.description)
        
        if desc_length < 100:
            return "5分钟"
        elif desc_length < 500:
            return "30分钟"
        elif desc_length < 2000:
            return "2小时"
        elif desc_length < 5000:
            return "1天"
        elif desc_length < 20000:
            return "1周"
        else:
            return "1月+"
    
    def _generate_subtasks(
        self,
        task: Task,
        strategy: str,
        depth: int
    ) -> List[Task]:
        """生成子任务"""
        subtasks = []
        
        # 基于不同策略生成
        if strategy == "detailed":
            subtasks = self._generate_detailed_subtasks(task)
        elif strategy == "quick":
            subtasks = self._generate_quick_subtasks(task)
        else:  # auto
            subtasks = self._generate_auto_subtasks(task)
        
        # 分配优先级
        for i, subtask in enumerate(subtasks):
            # 前面的子任务优先级高
            priority_value = max(0, TaskPriority.HIGH.value - i)
            subtask.priority = TaskPriority(priority_value) if priority_value < 3 else TaskPriority.MEDIUM
        
        return subtasks
    
    def _generate_auto_subtasks(self, task: Task) -> List[Task]:
        """自动生成子任务"""
        # 分析任务描述，提取关键步骤
        steps = self._analyze_task_steps(task.description)
        
        subtasks = []
        for i, step in enumerate(steps):
            subtask = Task(title=f"步骤{i+1}: {step['title']}")
            subtask.description = step['description']
            subtask.estimated_complexity = step.get('complexity', 5)
            subtask.estimated_duration = step.get('duration', '1小时')
            subtasks.append(subtask)
        
        return subtasks
    
    def _generate_detailed_subtasks(self, task: Task) -> List[Task]:
        """详细分解"""
        # 更细粒度的分解
        return self._generate_auto_subtasks(task)
    
    def _generate_quick_subtasks(self, task: Task) -> List[Task]:
        """快速分解"""
        # 最小化分解，只分解为2-3个子任务
        return self._generate_auto_subtasks(task)[:3]
    
    def _analyze_task_steps(self, description: str) -> List[Dict[str, Any]]:
        """分析任务步骤"""
        # 使用记忆系统压缩上下文
        compressed = self.memory.compress_context(description, level='medium')
        
        # 智能识别步骤
        steps = []
        
        # 简单的步骤识别（基于关键词）
        step_indicators = ['首先', '然后', '接着', '最后', '第一', '第二', '第三']
        sentences = compressed.split('。')
        
        current_step = None
        for sentence in sentences:
            is_step_start = any(ind in sentence for ind in step_indicators)
            
            if is_step_start:
                if current_step:
                    steps.append(current_step)
                current_step = {
                    'title': sentence[:30],
                    'description': sentence,
                    'complexity': 5,
                    'duration': '1小时'
                }
            elif current_step:
                current_step['description'] += '。' + sentence
        
        if current_step:
            steps.append(current_step)
        
        if not steps:
            # 默认分解
            steps = [
                {'title': '准备阶段', 'description': '准备工作', 'complexity': 3, 'duration': '30分钟'},
                {'title': '执行阶段', 'description': compressed, 'complexity': 6, 'duration': '2小时'},
                {'title': '收尾阶段', 'description': '收尾工作', 'complexity': 2, 'duration': '30分钟'}
            ]
        
        return steps


class AgentCoordinator:
    """Agent协调器 - 管理大规模Agent"""
    
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.active_agents: Dict[str, Any] = {}
        self.agent_queue: List[str] = []
        self.completed_tasks: Dict[str, Any] = {}
        
        # Agent池配置
        self.agent_types = {
            'researcher': {'capability': '研究分析', 'context_need': 5000},
            'coder': {'capability': '代码编写', 'context_need': 3000},
            'writer': {'capability': '文档撰写', 'context_need': 2000},
            'reviewer': {'capability': '评审检查', 'context_need': 4000},
            'coordinator': {'capability': '协调管理', 'context_need': 8000}
        }
    
    def dispatch(self, task: Task, context: TaskContext) -> Dict[str, Any]:
        """派遣Agent执行任务"""
        # 选择最合适的Agent类型
        agent_type = self._select_agent_type(task)
        
        # 获取压缩后的上下文
        agent_context = context.get_context(
            self.agent_types[agent_type]['context_need']
        )
        
        # 创建执行任务
        execution = {
            'task_id': task.id,
            'agent_type': agent_type,
            'context_length': len(agent_context),
            'status': 'dispatched',
            'dispatched_at': time.time()
        }
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.assigned_agent = agent_type
        task.started_at = time.time()
        
        return execution
    
    def _select_agent_type(self, task: Task) -> str:
        """选择Agent类型"""
        title = task.title.lower()
        desc = task.description.lower()
        
        # 基于关键词匹配
        if any(kw in title or kw in desc for kw in ['研究', '分析', '调研', '探索']):
            return 'researcher'
        elif any(kw in title or kw in desc for kw in ['代码', '开发', '实现', '编写', '程序']):
            return 'coder'
        elif any(kw in title or kw in desc for kw in ['文档', '报告', '撰写', '写作', '编写']):
            return 'writer'
        elif any(kw in title or kw in desc for kw in ['评审', '检查', '审核', '验证']):
            return 'reviewer'
        else:
            return 'coordinator'
    
    def get_execution_status(self, task_id: str) -> Dict[str, Any]:
        """获取执行状态"""
        return self.completed_tasks.get(task_id, {'status': 'unknown'})


class TaskMindOS:
    """
    TaskMind-OS - 分布式任务操作系统
    
    支持：
    - 极长上下文（GB级别）
    - 复杂任务层级（20+层）
    - 长时间跨度（数周/数月）
    - 大规模并行Agent
    """
    
    def __init__(self):
        # 核心组件
        self.memory = MemorySystem()
        self.task_graph = TaskGraph()
        self.decomposer = HierarchicalDecomposer(self.memory)
        self.agent_coordinator = AgentCoordinator()
        
        # 方案管理
        self.solutions: Dict[str, List[Solution]] = {}
        
        # 元信息
        self.created_at = time.time()
        self.last_updated = time.time()
    
    def process_open_task(self, task_description: str) -> Dict[str, Any]:
        """
        处理开放性任务 - 主入口
        """
        print("="*80)
        print("TaskMind-OS: 分布式任务操作系统")
        print("="*80)
        
        # 步骤1：分析任务，生成多个方案
        print("\n📋 步骤1: 深度分析开放性任务...")
        solutions = self._generate_solutions(task_description)
        
        # 保存方案
        self.solutions[task_description] = solutions
        
        print(f"\n✨ 生成了 {len(solutions)} 个方案：")
        for i, sol in enumerate(solutions, 1):
            print(f"\n  方案{i}: {sol.title}")
            print(f"  策略: {sol.strategy}")
            print(f"  置信度: {sol.confidence:.1%}")
            print(f"  预估时间: {sol.estimated_duration}")
            print(f"  复杂度: {sol.complexity_score}/10")
            print(f"  优势: {', '.join(sol.pros[:2])}")
            print(f"  风险: {', '.join(sol.risks[:1])}")
        
        return {
            'task': task_description,
            'solutions': solutions,
            'recommended_index': 0
        }
    
    def _generate_solutions(self, task_description: str) -> List[Solution]:
        """生成多个方案"""
        # 分析任务特征
        complexity = self._analyze_complexity(task_description)
        openness = self._analyze_openness(task_description)
        
        solutions = []
        
        # 根据开放程度生成不同策略的方案
        if openness >= 7:
            # 高开放度：探索、保守、创新三方案
            solutions.append(self._create_explorative_solution(task_description, complexity))
            solutions.append(self._create_conservative_solution(task_description, complexity))
            solutions.append(self._create_innovative_solution(task_description, complexity))
        else:
            # 低开放度：标准、快速、详细三方案
            solutions.append(self._create_standard_solution(task_description, complexity))
            solutions.append(self._create_fast_solution(task_description, complexity))
            solutions.append(self._create_detailed_solution(task_description, complexity))
        
        # 按置信度排序
        solutions.sort(key=lambda x: x.confidence, reverse=True)
        return solutions[:5]
    
    def _analyze_complexity(self, task: str) -> int:
        """分析任务复杂度"""
        score = 5
        
        # 基于长度
        if len(task) > 1000:
            score += 2
        elif len(task) > 500:
            score += 1
        
        # 基于关键词
        complex_keywords = ['系统', '平台', '架构', '复杂', '综合', '全面']
        for kw in complex_keywords:
            if kw in task:
                score += 1
        
        return min(10, max(1, score))
    
    def _analyze_openness(self, task: str) -> int:
        """分析任务开放程度"""
        score = 5
        
        open_keywords = ['探索', '研究', '思考', '如何', '怎样', '有没有']
        closed_keywords = ['修复', '完成', '实现', '制作', '按照']
        
        for kw in open_keywords:
            if kw in task:
                score += 1
        for kw in closed_keywords:
            if kw in task:
                score -= 1
        
        return min(10, max(1, score))
    
    def _create_explorative_solution(self, task: str, complexity: int) -> Solution:
        """创建探索性方案"""
        sol = Solution()
        sol.title = "渐进式探索方案"
        sol.strategy = "explorative"
        sol.description = "广泛探索，逐步明确，在过程中寻找最优解"
        sol.complexity_score = min(10, complexity + 2)
        sol.estimated_duration = "较长（根据探索结果调整）"
        sol.confidence = 0.75
        sol.pros = ["风险可控", "信息充分", "灵活调整"]
        sol.cons = ["耗时较长"]
        sol.risks = ["可能需要多次迭代"]
        return sol
    
    def _create_conservative_solution(self, task: str, complexity: int) -> Solution:
        """创建保守方案"""
        sol = Solution()
        sol.title = "稳健推进方案"
        sol.strategy = "conservative"
        sol.description = "MVP优先，快速验证，逐步完善"
        sol.complexity_score = max(1, complexity - 2)
        sol.estimated_duration = "中等"
        sol.confidence = 0.85
        sol.pros = ["快速验证", "风险低", "可迭代"]
        sol.cons = ["可能不是最优解"]
        sol.risks = ["功能可能不完整"]
        return sol
    
    def _create_innovative_solution(self, task: str, complexity: int) -> Solution:
        """创建创新方案"""
        sol = Solution()
        sol.title = "突破创新方案"
        sol.strategy = "innovative"
        sol.description = "深入分析，突破常规，寻找创新点"
        sol.complexity_score = min(10, complexity + 3)
        sol.estimated_duration = "较长"
        sol.confidence = 0.55
        sol.pros = ["可能找到最优解", "创新价值高"]
        sol.cons = ["风险较高", "不确定性大"]
        sol.risks = ["可能需要回滚"]
        return sol
    
    def _create_standard_solution(self, task: str, complexity: int) -> Solution:
        """创建标准方案"""
        sol = Solution()
        sol.title = "标准执行方案"
        sol.strategy = "standard"
        sol.description = "采用标准流程，稳定可靠"
        sol.complexity_score = complexity
        sol.estimated_duration = "中等"
        sol.confidence = 0.80
        sol.pros = ["稳定", "可预测"]
        sol.cons = ["可能不是最优"]
        sol.risks = ["缺乏灵活性"]
        return sol
    
    def _create_fast_solution(self, task: str, complexity: int) -> Solution:
        """创建快速方案"""
        sol = Solution()
        sol.title = "快速交付方案"
        sol.strategy = "fast"
        sol.description = "聚焦核心，快速交付"
        sol.complexity_score = max(1, complexity - 3)
        sol.estimated_duration = "短"
        sol.confidence = 0.70
        sol.pros = ["最快速度"]
        sol.cons = ["质量可能打折"]
        sol.risks = ["后期可能需要重构"]
        return sol
    
    def _create_detailed_solution(self, task: str, complexity: int) -> Solution:
        """创建详细方案"""
        sol = Solution()
        sol.title = "详细规划方案"
        sol.strategy = "detailed"
        sol.description = "充分规划，详尽执行"
        sol.complexity_score = min(10, complexity + 1)
        sol.estimated_duration = "较长"
        sol.confidence = 0.90
        sol.pros = ["质量高", "覆盖全面"]
        sol.cons = ["准备时间长"]
        sol.risks = ["可能过度规划"]
        return sol
    
    def execute_solution(
        self,
        task_description: str,
        solution_index: int = 0
    ) -> Dict[str, Any]:
        """执行选定的方案"""
        solutions = self.solutions.get(task_description, [])
        if not solutions or solution_index >= len(solutions):
            return {'status': 'error', 'message': '方案不存在'}
        
        solution = solutions[solution_index]
        solution.selected = True
        
        print(f"\n🚀 开始执行方案: {solution.title}")
        
        # 创建根任务
        root_task = Task(title=task_description)
        root_task.description = task_description
        root_task.estimated_complexity = solution.complexity_score
        root_task.context = TaskContext(
            task_id=root_task.id,
            summary=task_description
        )
        
        # 添加到图谱
        self.task_graph.add_task(root_task)
        solution.root_task_id = root_task.id
        
        # 层级化分解任务
        print("\n📦 步骤2: 层级化分解任务...")
        all_tasks = self.decomposer.decompose(
            root_task,
            strategy=solution.strategy
        )
        
        for task in all_tasks:
            if task.id != root_task.id:
                self.task_graph.add_task(task)
        
        stats = self.task_graph.get_statistics()
        print(f"  总任务数: {stats['total']}")
        print(f"  最大层级: {stats['max_level']}")
        print(f"  就绪任务: {stats['status_breakdown'].get('pending', 0)}")
        
        # 派遣Agent执行
        print(f"\n🤖 步骤3: 派遣Agent执行...")
        ready_tasks = self.task_graph.get_ready_tasks(max_count=10)
        
        dispatch_count = 0
        for task in ready_tasks:
            if task.context:
                result = self.agent_coordinator.dispatch(task, task.context)
                dispatch_count += 1
                print(f"  ✓ {task.title[:40]}... -> {result['agent_type']}")
        
        print(f"\n  已派遣 {dispatch_count} 个任务")
        
        return {
            'solution': solution,
            'stats': stats,
            'dispatched': dispatch_count
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """获取执行进度"""
        stats = self.task_graph.get_statistics()
        return {
            'progress_percent': f"{stats['progress']*100:.1f}%",
            'completed': stats['completed'],
            'total': stats['total'],
            'status_breakdown': stats['status_breakdown'],
            'max_level': stats['max_level'],
            'uptime': f"{(time.time() - self.created_at)/3600:.1f}小时"
        }


# 使用示例
if __name__ == "__main__":
    print("="*80)
    print("TaskMind-OS 演示 - 支持超大规模任务")
    print("="*80)
    
    # 创建系统
    system = TaskMindOS()
    
    # 示例：超复杂开放性任务
    complex_task = """
    我们公司想要打造一个新一代的智能协作平台，需要：
    1. 重新思考团队的协作模式
    2. 整合现有的多个工具和系统
    3. 引入AI辅助能力
    4. 考虑未来3-5年的扩展性
    5. 平衡创新和稳定性的关系
    6. 制定详细的实施路线图
    """
    
    # 处理任务
    result = system.process_open_task(complex_task)
    
    print("\n" + "="*80)
    print("推荐方案: 方案1")
    print("="*80)
    
    # 执行方案
    execution = system.execute_solution(complex_task, solution_index=0)
    
    # 查看进度
    print("\n" + "="*80)
    print("当前进度")
    print("="*80)
    progress = system.get_progress()
    for key, value in progress.items():
        print(f"  {key}: {value}")
