# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 1-1 zh
content = content.replace(
    '问题可以通过阅读视频中的某些帧来作答，无需时序理解或复杂推理。',
    '问题可通过阅读视频中的某些帧作答，无需理解时序或跨模态关联，属于 Level 1（信息检索与聚合）。',
    1
)
# Replace Short Films
content = content.replace(
    '<strong>一致性测评：</strong>测试视觉场景的<em>情感氛围</em>是否与背景音乐的<em>情绪基调</em>在逻辑上保持一致。',
    '<strong>能力一致性测评：</strong>4个问题均测试<em>跨模态语义一致性</em>（视频帧+音频），同一粒度但不同故事片段。问题可通过感知画面色调与背景音乐情绪的对应作答，无需时序推理，属于 Level 1（信息检索与聚合）。',
    1
)
# Replace Shell Game
content = content.replace(
    '<strong>一致性测评：</strong>测试<em>实体持久性</em>和<em>视角转换</em>。模型能否在多次交换中追踪隐藏物体，并在不同空间视角（表演者 vs 观众）间切换？',
    '<strong>能力一致性测评：</strong>4个问题均测试<em>实体持久性</em>与<em>视角转换</em>（物理世界推理），同一粒度但不同追踪目标。需在多次交换中追踪隐藏物体并在表演者/观众视角间切换，属于 Level 3（复杂推理）。',
    1
)
# Replace Geometry - 连贯性
content = content.replace(
    '<strong>连贯性测评：</strong>逻辑树 <code>[[1,2],3,4]</code>。Q1 和 Q2 求解独立变量。Q3 结合 Q1 和 Q2 计算总面积。Q4 从 Q3 推导最终值 A。',
    '<strong>推理连贯性测评：</strong>逻辑链 <code>[[1,2],3,4]</code>。4个问题均测试<em>数学逻辑</em>（知识获取）：Q1 和 Q2 求解独立变量，Q3 结合 Q1 和 Q2 计算总面积，Q4 从 Q3 推导最终值。需多步数学推导与逻辑链推理，属于 Level 3（复杂推理）。',
    1
)
# Replace Social Detox
content = content.replace(
    '<strong>一致性测评：</strong>测试<em>复杂剧情理解</em>。模型能否识别关键的心理转折点（决定隔离、尝试重新连接、再次陷入成瘾）？',
    '<strong>能力一致性测评：</strong>4个问题均测试<em>叙事转折点检测</em>（复杂剧情理解），同一粒度但不同转折点。需理解叙事中的心理与情节转折，属于 Level 3（复杂推理）。',
    1
)
# Replace Wood Carving
content = content.replace(
    '<strong>一致性测评：</strong>测试<em>基于视频的知识获取</em>。模型能否从教程中学会具体的技术细节（选材、镜像操作逻辑、错误分析、刀法辨析）？',
    '<strong>能力一致性测评：</strong>4个问题均测试<em>基于视频的知识获取</em>（通用技能），同一粒度但不同技术要点。需从教程视频中学习并应用技能，属于 Level 3（复杂推理）。',
    1
)
# Replace Water Gun - 连贯性
content = content.replace(
    '<strong>连贯性测评：</strong>线性逻辑链 <code>[1,2,3,4]</code>。Q1 确立淘汰判定规则 → Q2 识别首次阵亡场景 → Q3 分析攻击者准备动作 → Q4 进行反事实推理：<em>若玩家存活，将升级何武器并采取何战术？</em>',
    '<strong>推理连贯性测评：</strong>线性逻辑链 <code>[1,2,3,4]</code>。4个问题均测试<em>反事实推理</em>（物理世界推理）。Q1 确立规则 → Q2 识别阵亡场景 → Q3 分析攻击准备 → Q4 反事实推理。需理解游戏逻辑并进行假设推理，属于 Level 3（复杂推理）。',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
