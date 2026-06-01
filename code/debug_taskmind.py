"""
调试脚本：检查任务分解逻辑
"""

from taskmind_os_fixed import HierarchicalDecomposer, MemorySystem, Task, TaskStatus

# 创建组件
memory = MemorySystem()
decomposer = HierarchicalDecomposer(memory)

# 创建测试任务
test_task = Task(title="测试任务")
test_task.description = """
我们公司想要打造一个新一代的智能协作平台，需要：
1. 重新思考团队的协作模式
2. 整合现有的多个工具和系统
3. 引入AI辅助能力
4. 考虑未来3-5年的扩展性
5. 平衡创新和稳定性的关系
6. 制定详细的实施路线图
"""
test_task.estimated_complexity = 7

print("="*60)
print("调试任务分解逻辑")
print("="*60)

# 检查各个判断条件
print(f"\n任务复杂度: {test_task.estimated_complexity}")
print(f"复杂度 <= 3? {test_task.estimated_complexity <= 3}")

size = decomposer._estimate_task_size(test_task)
print(f"任务大小: {size}")
print(f"大小 <= '30分钟'? {size <= decomposer.min_task_size}")

should_decompose = decomposer._should_decompose(test_task, 0)
print(f"应该分解? {should_decompose}")

# 检查步骤分析
print("\n分析任务步骤:")
steps = decomposer._analyze_task_steps(test_task.description)
print(f"识别到 {len(steps)} 个步骤")
for i, step in enumerate(steps, 1):
    print(f"  步骤{i}: {step['title']}")

# 手动执行分解
print("\n手动执行分解:")
result = decomposer.decompose(test_task, strategy="standard", depth=0)
print(f"分解结果: {len(result)} 个任务")
for i, task in enumerate(result, 1):
    print(f"  任务{i}: {task.title} (层级: {task.level})")
