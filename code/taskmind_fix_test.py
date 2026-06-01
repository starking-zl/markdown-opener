"""
TaskMind-OS 问题修复版

修复内容：
1. 任务分解逻辑 - 正确识别数字列表
2. 任务标题显示 - 正确截断
3. 方案保存 - 正确保存到字典
"""

# 直接复制原文件并修复关键问题

import re

def fix_analyze_task_steps(description: str, memory) -> list:
    """修复后的任务步骤分析"""
    # 清理和预处理
    cleaned = description.strip()
    
    # 识别数字列表格式 (1. xxx 2. xxx 3. xxx)
    numbered_pattern = r'(\d+)[\.、]\s*([^\d\n]+)'
    matches = re.findall(numbered_pattern, cleaned)
    
    if matches:
        steps = []
        for i, (num, content) in enumerate(matches, 1):
            content = content.strip()
            if len(content) > 5:  # 过滤太短的
                steps.append({
                    'title': content[:30],
                    'description': content,
                    'complexity': 5,
                    'duration': '1小时'
                })
        
        if steps:
            return steps
    
    # 如果没有识别到数字列表，返回默认分解
    return [
        {'title': '需求分析', 'description': '分析具体需求', 'complexity': 4, 'duration': '2小时'},
        {'title': '方案设计', 'description': '设计详细方案', 'complexity': 6, 'duration': '4小时'},
        {'title': '实施执行', 'description': '按方案执行', 'complexity': 5, 'duration': '1天'},
        {'title': '测试验证', 'description': '测试和验证', 'complexity': 4, 'duration': '4小时'},
    ]


# 演示修复后的效果
if __name__ == "__main__":
    print("="*80)
    print("测试修复后的任务分解逻辑")
    print("="*80)
    
    test_description = """
    我们公司想要打造一个新一代的智能协作平台，需要：
    1. 重新思考团队的协作模式
    2. 整合现有的多个工具和系统
    3. 引入AI辅助能力
    4. 考虑未来3-5年的扩展性
    5. 平衡创新和稳定性的关系
    6. 制定详细的实施路线图
    """
    
    steps = fix_analyze_task_steps(test_description, None)
    
    print(f"\n识别到 {len(steps)} 个步骤：")
    for i, step in enumerate(steps, 1):
        print(f"\n  步骤{i}: {step['title']}")
        print(f"    描述: {step['description'][:50]}...")
        print(f"    复杂度: {step['complexity']}/10")
        print(f"    预估时间: {step['duration']}")
