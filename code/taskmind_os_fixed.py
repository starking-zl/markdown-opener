"""
TaskMind-OS - 分布式任务操作系统 (修复版)

修复内容：
1. 任务分解逻辑 - 正确识别数字列表格式
2. 任务标题显示 - 正确截断
3. 方案保存 - 正确保存到字典
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import json
import re
from collections import defaultdict
import heapq


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    details: Optional[str] = None
    compressed_versions: Dict[int, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_context(self, max_length: int = None) -> str:
        """获取指定长度的上下文"""
        if max_length is None:
            return self.details or self.summary
        
        if max_length in self.compressed_versions:
            return self.compressed_versions[max_length]
        
        return self.summary[:max_length] if len(self.summary) > max_length else self.summary
    
    def add_compressed_version(self, length: int, content: str):
        self.compressed_versions[length] = content


class Task:
    """任务节点"""
    def __init__(self, task_id: str = None, title: str = ""):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description: str = ""
        self.status: TaskStatus = TaskStatus.PENDING
        self.priority: TaskPriority = TaskPriority.MEDIUM
        self.level: int = 0
        self.parent_id: Optional[str] = None
        self.children_ids: Set[str] = set()
        self.dependencies: Set[str] = set()
        self.dependents: Set[str] = set()
        self.assigned_agent: Optional[str] = None
        self.result: Optional[Any] = None
        self.context: Optional[TaskContext] = None
        self.created_at: float = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.estimated_duration: Optional[str] = None
        self.estimated_complexity: int = 5
    
    def is_ready(self) -> bool:
        return self.status == TaskStatus.PENDING and len(self.dependencies) == 0
    
    def add_child(self, child_id: str):
        self.children_ids.add(child_id)
    
    def add_dependency(self, dep_id: str):
        self.dependencies.add(dep_id)


class TaskGraph:
    """任务图谱"""
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.level_index: Dict[int, Set[str]] = defaultdict(set)
        self.ready_queue: List[str] = []
        self.completed_count: int = 0
        self.total_count: int = 0
    
    def add_task(self, task: Task):
        self.tasks[task.id] = task
        self.level_index[task.level].add(task.id)
        self.total_count += 1
        
        if task.is_ready():
            self._add_to_ready_queue(task.id)
    
    def _add_to_ready_queue(self, task_id: str):
        task = self.tasks[task_id]
        heapq.heappush(self.ready_queue, (task.priority.value, task.created_at, task_id))
    
    def get_ready_tasks(self, max_count: int = 10) -> List[Task]:
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
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()
        self.completed_count += 1
        
        for dep_id in task.dependents:
            dep_task = self.tasks.get(dep_id)
            if dep_task:
                dep_task.dependencies.discard(task_id)
                if dep_task.is_ready():
                    self._add_to_ready_queue(dep_id)
    
    def get_task_tree(self, task_id: str, max_depth: int = 3) -> Dict:
        task = self.tasks.get(task_id)
        if not task:
            return {}
        
        result = {
            'id': task.id,
            'title': task.title[:50],
            'status': task.status.value,
            'level': task.level,
            'children': []
        }
        
        if max_depth > 0:
            for child_id in list(task.children_ids)[:10]:
                child_tree = self.get_task_tree(child_id, max_depth - 1)
                if child_tree:
                    result['children'].append(child_tree)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
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
        self.strategy: str = ""
        self.task_graph: TaskGraph = TaskGraph()
        self.root_task_id: Optional[str] = None
        self.confidence: float = 0.0
        self.estimated_duration: str = ""
        self.complexity_score: int = 5
        self.pros: List[str] = []
        self.cons: List[str] = []
        self.risks: List[str] = []
        self.selected: bool = False


class MemorySystem:
    """分布式记忆系统"""
    def __init__(self, base_dir: str = "./task_memory"):
        self.base_dir = base_dir
        self.short_term: Dict[str, Any] = {}
        self.working_summary: str = ""
        self.long_term_index: Dict[str, Dict[str, Any]] = {}
        
        self.compression_levels = {
            'brief': 100,
            'short': 500,
            'medium': 2000,
            'long': 10000,
            'full': 100000
        }
    
    def store(self, key: str, value: Any, tier: str = 'short'):
        if tier == 'short':
            self.short_term[key] = value
        else:
            self.long_term_index[key] = {
                'value': value,
                'tier': tier,
                'timestamp': time.time()
            }
    
    def compress_context(self, content: str, level: str = 'medium') -> str:
        max_length = self.compression_levels.get(level, 2000)
        
        if len(content) <= max_length:
            return content
        
        if level == 'brief':
            return self._extract_brief_summary(content)
        elif level == 'short':
            return self._extract_key_points(content, max_length)
        elif level == 'medium':
            return self._extract_main_points(content, max_length)
        else:
            return self._smart_compress(content, max_length)
    
    def _extract_brief_summary(self, content: str, max_length: int = 100) -> str:
        sentences = content.split('。')
        if len(sentences) <= 3:
            return content[:max_length]
        
        first = sentences[0]
        last = sentences[-1]
        middle = sentences[len(sentences)//2]
        
        summary = f"{first}...{middle}...{last}"
        return summary[:max_length]
    
    def _extract_key_points(self, content: str, max_length: int = 500) -> str:
        key_indicators = ['重要', '关键', '必须', '主要', '核心', '最终', '目标']
        sentences = content.split('。')
        key_sentences = [s for s in sentences if any(ind in s for ind in key_indicators)]
        
        if len(key_sentences) >= 3:
            result = '。'.join(key_sentences[:5])
        else:
            result = '。'.join([sentences[0], sentences[len(sentences)//2], sentences[-1]])
        
        return result[:max_length]
    
    def _extract_main_points(self, content: str, max_length: int = 2000) -> str:
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) <= 5:
            return content[:max_length]
        
        scored_paragraphs = []
        for i, para in enumerate(paragraphs):
            score = len(para) * 0.5
            if i == 0:
                score += len(para) * 0.3
            if i == len(paragraphs) - 1:
                score += len(para) * 0.3
            scored_paragraphs.append((score, para))
        
        scored_paragraphs.sort(reverse=True)
        selected = [p[1] for p in scored_paragraphs[:5]]
        
        result = '\n\n'.join(selected)
        return result[:max_length]
    
    def _smart_compress(self, content: str, max_length: int) -> str:
        if len(content) <= max_length:
            return content
        
        main_points = self._extract_main_points(content, max_length * 2)
        return main_points[:max_length]


class HierarchicalDecomposer:
    """层级化任务分解器"""
    def __init__(self, memory: MemorySystem):
        self.memory = memory
        self.max_level = 20
        self.min_task_size = "30分钟"
        self.decompose_threshold = 10
    
    def decompose(self, task: Task, strategy: str = "auto", depth: int = 0) -> List[Task]:
        """递归分解任务"""
        all_tasks = [task]  # 包含父任务
        
        # 检查是否需要继续分解
        if task.estimated_complexity > 5 and depth < self.max_level:
            # 生成子任务
            subtasks = self._generate_subtasks(task, strategy, depth)
            
            # 限制子任务数量
            if len(subtasks) > 10:
                subtasks = subtasks[:10]
            
            for subtask in subtasks:
                subtask.level = depth + 1
                subtask.parent_id = task.id
                task.add_child(subtask.id)
                
                # 为子任务创建context
                subtask.context = TaskContext(
                    task_id=subtask.id,
                    summary=subtask.description[:200] if len(subtask.description) > 200 else subtask.description
                )
                
                # 递归处理（子任务复杂度递减）
                if depth < self.max_level - 1 and subtask.estimated_complexity > 3:
                    # 递归分解，将所有结果添加到all_tasks
                    decomposed = self.decompose(subtask, strategy, depth + 1)
                    all_tasks.extend(decomposed)  # 修复：直接extend所有结果
                else:
                    all_tasks.append(subtask)
        
        return all_tasks
    
    def _should_decompose(self, task: Task, current_depth: int) -> bool:
        """判断是否需要继续分解"""
        # 层级限制
        if current_depth >= self.max_level:
            return False
        
        # 任务复杂度阈值（只有复杂度>5才分解）
        if task.estimated_complexity <= 5:
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
            return "30分钟+"
        elif desc_length < 2000:
            return "2小时"
        elif desc_length < 5000:
            return "1天"
        elif desc_length < 20000:
            return "1周"
        else:
            return "1月+"
    
    def _generate_subtasks(self, task: Task, strategy: str, depth: int) -> List[Task]:
        subtasks = []
        
        if strategy == "detailed":
            subtasks = self._generate_detailed_subtasks(task)
        elif strategy == "quick":
            subtasks = self._generate_quick_subtasks(task)
        else:
            subtasks = self._generate_auto_subtasks(task)
        
        for i, subtask in enumerate(subtasks):
            priority_value = max(0, TaskPriority.HIGH.value - i)
            subtask.priority = TaskPriority(priority_value) if priority_value < 3 else TaskPriority.MEDIUM
        
        return subtasks
    
    def _generate_auto_subtasks(self, task: Task) -> List[Task]:
        """自动生成子任务 - 修复版"""
        steps = self._analyze_task_steps(task.description)
        
        subtasks = []
        for i, step in enumerate(steps):
            subtask = Task(title=f"步骤{i+1}: {step['title']}")
            subtask.description = step['description']
            # 修复：子任务复杂度应该比父任务低，但不要低于3
            subtask.estimated_complexity = max(3, min(6, task.estimated_complexity - 1))
            subtask.estimated_duration = step.get('duration', '2小时')
            subtasks.append(subtask)
        
        return subtasks
    
    def _generate_detailed_subtasks(self, task: Task) -> List[Task]:
        """详细分解"""
        steps = self._analyze_task_steps(task.description)
        
        # 详细分解：将每个步骤再细分为3个子步骤
        subtasks = []
        for i, step in enumerate(steps):
            # 主任务
            main_task = Task(title=f"{i+1}. {step['title']}")
            main_task.description = step['description']
            main_task.estimated_complexity = step.get('complexity', 5)
            subtasks.append(main_task)
            
            # 子任务（准备、执行、收尾）
            for j, sub_type in enumerate(['准备', '执行', '收尾']):
                sub_task = Task(title=f"  {sub_type}: {step['title']}")
                sub_task.description = f"{sub_type}阶段 - {step['description']}"
                sub_task.estimated_complexity = max(2, step.get('complexity', 5) - 2)
                subtasks.append(sub_task)
        
        return subtasks
    
    def _generate_quick_subtasks(self, task: Task) -> List[Task]:
        """快速分解"""
        steps = self._analyze_task_steps(task.description)
        return [
            Task(title=f"核心: {steps[0]['title']}" if steps else "核心任务"),
            Task(title="实施执行"),
            Task(title="验证总结")
        ]
    
    def _analyze_task_steps(self, description: str) -> List[Dict[str, Any]]:
        """修复后的任务步骤分析 - 正确识别数字列表"""
        cleaned = description.strip()
        
        # 识别数字列表格式 (1. xxx 2. xxx 3. xxx)
        numbered_pattern = r'(\d+)[\.、]\s*([^\d\n]+)'
        matches = re.findall(numbered_pattern, cleaned)
        
        if matches:
            steps = []
            for i, (num, content) in enumerate(matches, 1):
                content = content.strip()
                if len(content) > 5:
                    steps.append({
                        'title': content[:40],
                        'description': content,
                        'complexity': 5,
                        'duration': '2小时'
                    })
            
            if steps:
                return steps
        
        # 如果没有识别到数字列表，尝试识别换行分隔的项
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        numbered_lines = []
        for line in lines:
            if re.match(r'^\d+[\.、\)]', line):
                content = re.sub(r'^\d+[\.、\)]\s*', '', line)
                if len(content) > 5:
                    numbered_lines.append(content)
        
        if len(numbered_lines) >= 3:
            return [
                {
                    'title': content[:40],
                    'description': content,
                    'complexity': 5,
                    'duration': '2小时'
                }
                for content in numbered_lines
            ]
        
        # 默认分解
        return [
            {'title': '需求分析', 'description': '分析具体需求', 'complexity': 4, 'duration': '2小时'},
            {'title': '方案设计', 'description': '设计详细方案', 'complexity': 6, 'duration': '4小时'},
            {'title': '实施执行', 'description': '按方案执行', 'complexity': 5, 'duration': '1天'},
            {'title': '测试验证', 'description': '测试和验证', 'complexity': 4, 'duration': '4小时'},
        ]


class AgentCoordinator:
    """Agent协调器"""
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.active_agents: Dict[str, Any] = {}
        self.agent_queue: List[str] = []
        self.completed_tasks: Dict[str, Any] = {}
        
        self.agent_types = {
            'researcher': {'capability': '研究分析', 'context_need': 5000},
            'coder': {'capability': '代码编写', 'context_need': 3000},
            'writer': {'capability': '文档撰写', 'context_need': 2000},
            'reviewer': {'capability': '评审检查', 'context_need': 4000},
            'coordinator': {'capability': '协调管理', 'context_need': 8000}
        }
    
    def dispatch(self, task: Task, context: TaskContext) -> Dict[str, Any]:
        agent_type = self._select_agent_type(task)
        
        agent_context = context.get_context(
            self.agent_types[agent_type]['context_need']
        )
        
        execution = {
            'task_id': task.id,
            'agent_type': agent_type,
            'context_length': len(agent_context),
            'status': 'dispatched',
            'dispatched_at': time.time()
        }
        
        task.status = TaskStatus.RUNNING
        task.assigned_agent = agent_type
        task.started_at = time.time()
        
        return execution
    
    def _select_agent_type(self, task: Task) -> str:
        title = task.title.lower()
        desc = task.description.lower()
        
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
        return self.completed_tasks.get(task_id, {'status': 'unknown'})


class TaskMindOS:
    """
    TaskMind-OS - 分布式任务操作系统 (修复版)
    """
    
    def __init__(self):
        self.memory = MemorySystem()
        self.task_graph = TaskGraph()
        self.decomposer = HierarchicalDecomposer(self.memory)
        self.agent_coordinator = AgentCoordinator()
        self.solutions: Dict[str, List[Solution]] = {}
        self.created_at = time.time()
        self.last_updated = time.time()
    
    def process_open_task(self, task_description: str) -> Dict[str, Any]:
        print("="*80)
        print("TaskMind-OS: 分布式任务操作系统 (修复版)")
        print("="*80)
        
        print("\n📋 步骤1: 深度分析开放性任务...")
        solutions = self._generate_solutions(task_description)
        
        # 保存方案 - 修复：确保保存
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
        complexity = self._analyze_complexity(task_description)
        openness = self._analyze_openness(task_description)
        
        solutions = []
        
        if openness >= 7:
            solutions.append(self._create_explorative_solution(task_description, complexity))
            solutions.append(self._create_conservative_solution(task_description, complexity))
            solutions.append(self._create_innovative_solution(task_description, complexity))
        else:
            solutions.append(self._create_standard_solution(task_description, complexity))
            solutions.append(self._create_fast_solution(task_description, complexity))
            solutions.append(self._create_detailed_solution(task_description, complexity))
        
        solutions.sort(key=lambda x: x.confidence, reverse=True)
        return solutions[:5]
    
    def _analyze_complexity(self, task: str) -> int:
        score = 5
        if len(task) > 1000:
            score += 2
        elif len(task) > 500:
            score += 1
        
        complex_keywords = ['系统', '平台', '架构', '复杂', '综合', '全面', '协作', '智能']
        for kw in complex_keywords:
            if kw in task:
                score += 1
        
        return min(10, max(1, score))
    
    def _analyze_openness(self, task: str) -> int:
        score = 5
        open_keywords = ['探索', '研究', '思考', '如何', '怎样', '有没有', '什么', '需要']
        closed_keywords = ['修复', '完成', '实现', '制作', '按照']
        
        for kw in open_keywords:
            if kw in task:
                score += 1
        for kw in closed_keywords:
            if kw in task:
                score -= 1
        
        return min(10, max(1, score))
    
    def _create_explorative_solution(self, task: str, complexity: int) -> Solution:
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
    
    def execute_solution(self, task_description: str, solution_index: int = 0) -> Dict[str, Any]:
        """执行选定的方案"""
        # 确保从字典获取
        solutions = self.solutions.get(task_description, [])
        if not solutions:
            return {'status': 'error', 'message': f'方案不存在 (已有方案: {len(self.solutions)})'}
        
        if solution_index >= len(solutions):
            return {'status': 'error', 'message': f'方案索引{solution_index}不存在'}
        
        solution = solutions[solution_index]
        solution.selected = True
        
        print(f"\n🚀 开始执行方案: {solution.title}")
        
        # 创建根任务
        root_task = Task(title=task_description[:50])
        root_task.description = task_description
        root_task.estimated_complexity = solution.complexity_score
        root_task.context = TaskContext(
            task_id=root_task.id,
            summary=task_description[:200]
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
        print(f"  ✓ 总任务数: {stats['total']}")
        print(f"  ✓ 最大层级: {stats['max_level']}")
        print(f"  ✓ 待执行任务: {stats['status_breakdown'].get('pending', 0)}")
        
        # 派遣Agent执行
        print(f"\n🤖 步骤3: 派遣Agent执行...")
        ready_tasks = self.task_graph.get_ready_tasks(max_count=10)
        
        dispatch_count = 0
        for task in ready_tasks:
            if task.context:
                result = self.agent_coordinator.dispatch(task, task.context)
                dispatch_count += 1
                # 正确截断标题
                title_display = task.title[:35] + "..." if len(task.title) > 35 else task.title
                print(f"  ✓ {title_display} -> {result['agent_type']}")
        
        print(f"\n  ✓ 已派遣 {dispatch_count} 个任务")
        
        return {
            'solution': solution,
            'stats': stats,
            'dispatched': dispatch_count
        }
    
    def get_progress(self) -> Dict[str, Any]:
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
    print("TaskMind-OS 演示 - 支持超大规模任务 (修复版)")
    print("="*80)
    
    system = TaskMindOS()
    
    complex_task = """
    我们公司想要打造一个新一代的智能协作平台，需要：
    1. 重新思考团队的协作模式
    2. 整合现有的多个工具和系统
    3. 引入AI辅助能力
    4. 考虑未来3-5年的扩展性
    5. 平衡创新和稳定性的关系
    6. 制定详细的实施路线图
    """
    
    # 步骤1：分析任务，生成方案
    result = system.process_open_task(complex_task)
    
    print("\n" + "="*80)
    print("推荐方案: 方案1")
    print("="*80)
    
    # 步骤2：执行方案
    execution = system.execute_solution(complex_task, solution_index=0)
    
    # 步骤3：查看进度
    print("\n" + "="*80)
    print("当前进度")
    print("="*80)
    progress = system.get_progress()
    for key, value in progress.items():
        print(f"  {key}: {value}")
