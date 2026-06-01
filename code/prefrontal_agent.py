"""
受前额叶启发的Agent架构 - Prefrontal Inspired Agent Architecture

这个框架模仿人类大脑的认知机制，核心功能包括：
1. 注意力过滤（类似前额叶的信息筛选）
2. 工作记忆（类似工作记忆系统）
3. 执行控制（类似前额叶的决策功能）
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AttentionPriority(Enum):
    """注意力优先级枚举"""
    CRITICAL = 0    # 关键信息
    HIGH = 1        # 高优先级
    MEDIUM = 2      # 中优先级
    LOW = 3         # 低优先级
    IGNORE = 4      # 忽略


@dataclass
class InputSignal:
    """输入信号 - 模拟视觉、听觉等感官输入"""
    id: str
    content: Any
    signal_type: str  # 'visual', 'audio', 'text', 'sensory', etc.
    timestamp: float = field(default_factory=time.time)
    raw_intensity: float = 0.5  # 原始信号强度
    priority: AttentionPriority = AttentionPriority.MEDIUM


@dataclass
class MemoryItem:
    """工作记忆项"""
    id: str
    content: Any
    priority: AttentionPriority
    timestamp: float
    expiration_time: Optional[float] = None  # 过期时间
    access_count: int = 0


class PrefrontalCortex:
    """前额叶模拟 - 执行控制中心"""
    
    def __init__(self, attention_bandwidth: int = 10, working_memory_capacity: int = 7):
        """
        初始化前额叶
        
        Args:
            attention_bandwidth: 注意力带宽（比特/秒，默认10bps）
            working_memory_capacity: 工作记忆容量（默认7±2）
        """
        self.attention_bandwidth = attention_bandwidth
        self.working_memory_capacity = working_memory_capacity
        self.working_memory: Dict[str, MemoryItem] = {}
        self.long_term_memory: List[Dict] = []
        self.execution_queue: List[Dict] = []
        
    def filter_input(self, signals: List[InputSignal]) -> List[InputSignal]:
        """
        过滤输入信号 - 模拟注意力筛选
        
        Args:
            signals: 所有输入信号
            
        Returns:
            筛选后的信号
        """
        # 按优先级排序
        prioritized = self._prioritize_signals(signals)
        
        # 带宽限制 - 只允许有限信息通过
        filtered = self._apply_bandwidth_constraint(prioritized)
        
        return filtered
    
    def _prioritize_signals(self, signals: List[InputSignal]) -> List[InputSignal]:
        """给信号分配优先级"""
        # 简单的优先级规则（实际可由更复杂的模型决定）
        prioritized = []
        for signal in signals:
            # 基于内容类型和强度的启发式优先级
            priority = AttentionPriority.MEDIUM
            content_str = str(signal.content).lower()
            
            # 示例规则
            if 'urgent' in content_str or 'emergency' in content_str:
                priority = AttentionPriority.CRITICAL
            elif signal.raw_intensity > 0.8:
                priority = AttentionPriority.HIGH
            elif signal.raw_intensity < 0.2:
                priority = AttentionPriority.LOW
                
            # 附加优先级信息
            signal.priority = priority
            prioritized.append(signal)
            # print(f"信号: {signal.content} -> 优先级: {priority.name}")
            
        # 按优先级排序
        prioritized.sort(key=lambda x: x.priority.value)
        return prioritized
    
    def _apply_bandwidth_constraint(self, signals: List[InputSignal]) -> List[InputSignal]:
        """应用带宽限制 - 10bit瓶颈模拟"""
        # 这里用简化的方式：只处理最高优先级的信号
        # 实际可以根据信息量计算
        max_processable = min(5, len(signals))  # 一次最多处理5个信号
        return signals[:max_processable]
    
    def update_working_memory(self, signals: List[InputSignal]):
        """更新工作记忆"""
        current_time = time.time()
        
        # 清理过期的记忆
        self._clean_expired_memory()
        
        # 按优先级从高到低添加新信号
        for signal in signals:
            if len(self.working_memory) >= self.working_memory_capacity:
                # 移除优先级最低的
                self._evict_low_priority_memory()
                
            memory_item = MemoryItem(
                id=signal.id,
                content=signal.content,
                priority=signal.priority,
                timestamp=signal.timestamp,
                expiration_time=current_time + 300  # 5分钟过期
            )
            self.working_memory[signal.id] = memory_item
    
    def _clean_expired_memory(self):
        """清理过期记忆"""
        current_time = time.time()
        expired_ids = [
            mid for mid, item in self.working_memory.items()
            if item.expiration_time and item.expiration_time < current_time
        ]
        for mid in expired_ids:
            del self.working_memory[mid]
    
    def _evict_low_priority_memory(self):
        """移除优先级最低的记忆项"""
        if not self.working_memory:
            return
            
        # 按优先级和访问次数排序（priority.value大表示优先级低）
        sorted_items = sorted(
            self.working_memory.items(),
            key=lambda x: (x[1].priority.value, -x[1].access_count)
        )
        
        # 移除优先级最低的（排在最后的）
        if sorted_items:
            del self.working_memory[sorted_items[-1][0]]
    
    def retrieve_from_memory(self, query: str) -> List[MemoryItem]:
        """从工作记忆中检索相关内容"""
        # 简单的检索逻辑
        results = []
        for item in self.working_memory.values():
            if query.lower() in str(item.content).lower():
                item.access_count += 1
                results.append(item)
        return results
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行决策 - 类似前额叶的执行控制"""
        # 模拟决策过程
        decision = {
            'action': 'process',
            'focus': 'current_task',
            'confidence': 0.7,
            'timestamp': time.time(),
            'working_memory_used': len(self.working_memory)
        }
        return decision


class SensoryCortex:
    """感觉皮层模拟 - 处理各种输入"""
    
    def process_visual(self, visual_data: Any) -> InputSignal:
        """处理视觉输入"""
        return InputSignal(
            id=f"visual_{uuid.uuid4().hex[:8]}",
            content=visual_data,
            signal_type='visual',
            raw_intensity=0.7
        )
    
    def process_audio(self, audio_data: Any) -> InputSignal:
        """处理听觉输入"""
        return InputSignal(
            id=f"audio_{uuid.uuid4().hex[:8]}",
            content=audio_data,
            signal_type='audio',
            raw_intensity=0.5
        )
    
    def process_text(self, text_data: str) -> InputSignal:
        """处理文本输入"""
        return InputSignal(
            id=f"text_{uuid.uuid4().hex[:8]}",
            content=text_data,
            signal_type='text',
            raw_intensity=0.6 if len(text_data) > 10 else 0.3
        )


class PrefrontalAgent:
    """完整的前额叶启发Agent"""
    
    def __init__(self):
        self.prefrontal = PrefrontalCortex()
        self.sensory = SensoryCortex()
        self.state = 'idle'
        
    def perceive_and_act(self, inputs: List[Dict[str, Any]]):
        """感知-行动循环"""
        # 1. 处理输入信号
        signals = []
        for input_data in inputs:
            if input_data['type'] == 'visual':
                signals.append(self.sensory.process_visual(input_data['data']))
            elif input_data['type'] == 'audio':
                signals.append(self.sensory.process_audio(input_data['data']))
            elif input_data['type'] == 'text':
                signals.append(self.sensory.process_text(input_data['data']))
        
        # 2. 前额叶过滤
        filtered_signals = self.prefrontal.filter_input(signals)
        
        # 3. 更新工作记忆
        self.prefrontal.update_working_memory(filtered_signals)
        
        # 4. 执行决策
        context = {
            'filtered_signals': filtered_signals,
            'state': self.state
        }
        decision = self.prefrontal.make_decision(context)
        
        return {
            'filtered_count': len(filtered_signals),
            'total_inputs': len(inputs),
            'decision': decision,
            'working_memory_size': len(self.prefrontal.working_memory)
        }


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Prefrontal Inspired Agent Demo")
    print("=" * 60)
    
    # 创建Agent
    agent = PrefrontalAgent()
    
    # 模拟大量输入信号
    inputs = [
        {'type': 'text', 'data': 'URGENT: System critical failure detected!'},
        {'type': 'text', 'data': '普通通知：今天会议改期'},
        {'type': 'visual', 'data': {'scene': 'office', 'people': 5}},
        {'type': 'text', 'data': '无关消息：促销广告'},
        {'type': 'text', 'data': '重要邮件：项目截止日期提醒'},
        {'type': 'audio', 'data': 'background_noise'},
        {'type': 'text', 'data': 'EMERGENCY: Fire alarm activated!'},
        {'type': 'visual', 'data': {'temperature': 25, 'humidity': 60}},
    ]
    
    print(f"\n输入信号数: {len(inputs)}")
    print("\n处理中...")
    
    # Agent感知和行动
    result = agent.perceive_and_act(inputs)
    
    print(f"\n过滤后信号数: {result['filtered_count']}")
    print(f"工作记忆使用量: {result['working_memory_size']}")
    print(f"决策结果: {json.dumps(result['decision'], indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("工作记忆内容:")
    print("=" * 60)
    for mid, item in agent.prefrontal.working_memory.items():
        print(f"- [{item.priority.name}] {str(item.content)[:50]}...")
