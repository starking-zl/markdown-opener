"""
多处理器Agent架构 - Multi-Processor Agent Architecture

核心概念：
1. 多个并行处理单元（模拟大脑各功能区）
2. 统一协调器（类似前额叶的"漏斗"）
3. 串行意识瓶颈（10bit/s）

架构灵感来自：
- 冷却报告视频："10bit信息如何卡住你的大脑"
- 人类大脑：多区域并行 + 意识串行瓶颈
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class AttentionPriority(Enum):
    """注意力优先级"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    IGNORE = 4


@dataclass
class Signal:
    """信息信号"""
    id: str
    source_processor: str  # 来源处理器
    content: Any
    signal_type: str
    timestamp: float = field(default_factory=time.time)
    intensity: float = 0.5
    priority: AttentionPriority = AttentionPriority.MEDIUM


class ParallelProcessor:
    """并行处理器 - 模拟大脑各功能区"""
    
    def __init__(self, name: str, processor_type: str, capacity: int = 100):
        self.name = name
        self.processor_type = processor_type
        self.capacity = capacity
        self.processing_queue = deque(maxlen=capacity)
        self.output_buffer = []
        
    def process_input(self, data: Any) -> List[Signal]:
        """处理输入并生成信号"""
        # 模拟各类型处理器的专门处理
        if self.processor_type == 'visual':
            processed = self._process_visual(data)
        elif self.processor_type == 'audio':
            processed = self._process_audio(data)
        elif self.processor_type == 'text':
            processed = self._process_text(data)
        elif self.processor_type == 'memory':
            processed = self._process_memory(data)
        elif self.processor_type == 'emotion':
            processed = self._process_emotion(data)
        else:
            processed = self._process_generic(data)
            
        return processed
    
    def _process_visual(self, data: Any) -> List[Signal]:
        """视觉处理器 - 大量并行处理"""
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=f"视觉特征: {str(data)[:30]}",
                signal_type='visual',
                intensity=0.7
            )
        ]
    
    def _process_audio(self, data: Any) -> List[Signal]:
        """听觉处理器"""
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=f"声音: {str(data)[:30]}",
                signal_type='audio',
                intensity=0.6
            )
        ]
    
    def _process_text(self, data: str) -> List[Signal]:
        """文本处理器"""
        urgency_keywords = ['urgent', 'emergency', '重要', '紧急']
        intensity = 0.5
        if any(kw in str(data).lower() for kw in urgency_keywords):
            intensity = 0.9
            
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=data,
                signal_type='text',
                intensity=intensity
            )
        ]
    
    def _process_memory(self, data: Any) -> List[Signal]:
        """记忆处理器 - 检索相关记忆"""
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=f"记忆回溯: {str(data)[:30]}",
                signal_type='memory',
                intensity=0.4
            )
        ]
    
    def _process_emotion(self, data: Any) -> List[Signal]:
        """情绪处理器"""
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=f"情绪信号: {str(data)[:30]}",
                signal_type='emotion',
                intensity=0.5
            )
        ]
    
    def _process_generic(self, data: Any) -> List[Signal]:
        """通用处理"""
        return [
            Signal(
                id=f"{self.name}_{uuid.uuid4().hex[:6]}",
                source_processor=self.name,
                content=str(data)[:50],
                signal_type='generic',
                intensity=0.5
            )
        ]


class PrefrontalFunnel:
    """前额叶漏斗 - 核心协调器
    
    这是模拟大脑的"10bit瓶颈"：
    - 接收所有并行处理器的输出
    - 通过优先级筛选
    - 串行化输出到意识层面
    """
    
    def __init__(self, bandwidth: int = 10, working_memory_capacity: int = 7):
        self.bandwidth = bandwidth  # 10 bit/s 瓶颈
        self.working_memory_capacity = working_memory_capacity
        self.working_memory: Dict[str, Signal] = {}
        self.long_term_storage = []
        self.processing_history = []
        
    def receive_signals(self, signals: List[Signal]) -> List[Signal]:
        """接收所有处理器的信号"""
        # 1. 批量接收（并行阶段）
        print(f"\n【漏斗接收】来自 {len(set(s.source_processor for s in signals))} 个处理器的 {len(signals)} 个信号")
        
        # 2. 优先级分配
        prioritized = self._assign_priorities(signals)
        
        # 3. 带宽限制 - 10bit瓶颈（串行阶段）
        filtered = self._apply_bandwidth_constraint(prioritized)
        
        print(f"【漏斗输出】经过瓶颈筛选，输出 {len(filtered)} 个信号到意识")
        
        return filtered
    
    def _assign_priorities(self, signals: List[Signal]) -> List[Signal]:
        """给信号分配优先级"""
        for signal in signals:
            # 基于强度和类型分配优先级
            if signal.intensity > 0.85:
                signal.priority = AttentionPriority.CRITICAL
            elif signal.intensity > 0.7:
                signal.priority = AttentionPriority.HIGH
            elif signal.intensity > 0.4:
                signal.priority = AttentionPriority.MEDIUM
            else:
                signal.priority = AttentionPriority.LOW
                
        # 按优先级排序
        signals.sort(key=lambda x: x.priority.value)
        return signals
    
    def _apply_bandwidth_constraint(self, signals: List[Signal]) -> List[Signal]:
        """应用10bit/s带宽限制"""
        # 简化为每次最多处理5个信号
        return signals[:min(self.bandwidth, len(signals))]
    
    def update_working_memory(self, signals: List[Signal]):
        """更新工作记忆"""
        current_time = time.time()
        
        # 清理过期记忆
        self._clean_expired()
        
        # 添加新信号
        for signal in signals:
            if len(self.working_memory) >= self.working_memory_capacity:
                # 淘汰低优先级
                self._evict_low_priority()
            
            self.working_memory[signal.id] = signal
            
        # 历史记录
        self.processing_history.extend(signals)
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
    
    def _clean_expired(self):
        """清理过期记忆"""
        # 简化版：直接清空
        pass
    
    def _evict_low_priority(self):
        """淘汰最低优先级"""
        if not self.working_memory:
            return
        
        # 找最低优先级
        lowest_priority_item = max(
            self.working_memory.items(),
            key=lambda x: x[1].priority.value
        )
        del self.working_memory[lowest_priority_item[0]]
    
    def conscious_output(self) -> Dict[str, Any]:
        """意识输出 - 最终串行结果"""
        return {
            'conscious_content': [s.content for s in self.working_memory.values()],
            'bandwidth_used': len(self.working_memory),
            'processing_snapshot': {
                'total_processors': 5,
                'active_signals': len(self.processing_history)
            }
        }


class MultiProcessorAgent:
    """多处理器Agent - 完整架构
    
    类比人类大脑的信息处理流程：
    1. 多个感官处理器并行工作（视觉、听觉、记忆等）
    2. 所有输出汇聚到前额叶漏斗
    3. 漏斗执行10bit/s的串行化瓶颈
    4. 输出到意识层面
    """
    
    def __init__(self):
        # 初始化多个并行处理器
        self.processors = {
            'visual': ParallelProcessor('视觉皮层', 'visual'),
            'audio': ParallelProcessor('听觉皮层', 'audio'),
            'text': ParallelProcessor('语言皮层', 'text'),
            'memory': ParallelProcessor('海马体', 'memory'),
            'emotion': ParallelProcessor('杏仁核', 'emotion'),
        }
        
        # 前额叶漏斗（协调器）
        self.prefrontal = PrefrontalFunnel()
        
        self.state = 'idle'
        
    def perceive_and_integrate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """完整的感知-整合流程"""
        print("\n" + "="*60)
        print("多处理器Agent 感知-整合流程")
        print("="*60)
        
        # 阶段1：并行处理
        print("\n【阶段1】并行处理（模拟大脑各功能区）")
        all_signals = []
        
        for input_type, data in inputs.items():
            if input_type in self.processors:
                signals = self.processors[input_type].process_input(data)
                all_signals.extend(signals)
                print(f"  {self.processors[input_type].name}: 处理 {len(signals)} 个信号")
        
        # 阶段2：漏斗过滤
        print("\n【阶段2】前额叶漏斗过滤（10bit/s瓶颈）")
        filtered_signals = self.prefrontal.receive_signals(all_signals)
        
        # 阶段3：工作记忆更新
        print("\n【阶段3】更新工作记忆")
        self.prefrontal.update_working_memory(filtered_signals)
        
        # 阶段4：意识输出
        print("\n【阶段4】意识输出")
        conscious_output = self.prefrontal.conscious_output()
        
        # 最终结果
        result = {
            'parallel_processors': len(self.processors),
            'total_signals_generated': len(all_signals),
            'signals_through_bottleneck': len(filtered_signals),
            'bandwidth_constraint': '10 bit/s (simulated)',
            'conscious_output': conscious_output,
            'timestamp': time.time()
        }
        
        return result


# 演示代码
if __name__ == "__main__":
    print("="*70)
    print("多处理器Agent架构演示")
    print("="*70)
    
    # 创建Agent
    agent = MultiProcessorAgent()
    
    # 模拟多模态输入
    inputs = {
        'visual': {'scene': '办公室', 'objects': ['电脑', '桌子']},
        'audio': '同事的讨论声',
        'text': 'URGENT: 项目deadline提前了！',
        'memory': '之前的项目经验',
        'emotion': '轻微压力'
    }
    
    print(f"\n输入类型: {list(inputs.keys())}")
    
    # 执行感知-整合
    result = agent.perceive_and_integrate(inputs)
    
    # 输出结果
    print("\n" + "="*70)
    print("处理结果摘要")
    print("="*70)
    print(f"并行处理器数量: {result['parallel_processors']}")
    print(f"生成的总信号数: {result['total_signals_generated']}")
    print(f"通过瓶颈的信号: {result['signals_through_bottleneck']}")
    print(f"带宽约束: {result['bandwidth_constraint']}")
    
    print("\n意识层面的内容:")
    for i, content in enumerate(result['conscious_output']['conscious_content'], 1):
        print(f"  {i}. {content}")
