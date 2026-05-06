# 旅渡 TravelDu V1 Prompt 设计文档

## 1. 本阶段目标

第五步的目标是把 DeepSeek 从“聊天模型”约束成“结构化规划组件”。V1 中 DeepSeek 不直接编造路线，也不直接决定真实距离和交通时间，而是承担以下任务：

1. 将用户自然语言需求解析为结构化旅行意图；
2. 将用户粘贴的攻略文本抽取为结构化 POI 候选信息；
3. 根据后端已生成的路线数据生成自然语言解释；
4. 根据用户调整指令生成结构化调整意图；
5. 必要时输出工具调用参数，由后端执行高德 POI、路线和天气查询。

DeepSeek JSON Output 要设置 `response_format={"type":"json_object"}`，并且 system 或 user prompt 中必须包含 `json` 字样和期望 JSON 示例；同时需要合理设置 `max_tokens`，避免 JSON 被截断。Function Calling / Tool Calls 中，模型只负责返回工具调用请求，具体外部函数必须由后端执行。

---

## 2. Prompt 文件清单

```text
backend/app/prompts/
  intent_parser.md
  note_extractor.md
  itinerary_explainer.md
  route_adjuster.md
  tool_decision.md
```

| 文件 | 作用 | 输入 | 输出 |
|---|---|---|---|
| `intent_parser.md` | 用户旅行需求解析 | 用户自然语言 | 旅行意图 JSON |
| `note_extractor.md` | 攻略文本 POI 抽取 | 攻略文本 | POI 列表 JSON |
| `itinerary_explainer.md` | 行程解释生成 | 已规划路线 JSON | 解释文本 JSON |
| `route_adjuster.md` | 用户调整指令解析 | 调整语句 + 当前行程摘要 | 调整意图 JSON |
| `tool_decision.md` | 工具调用决策 | 任务状态 JSON | 工具调用建议 JSON |

---

## 3. 全局设计原则

### 3.1 先结构化，再生成文本

所有 DeepSeek 输出必须先转成 JSON，再进入业务逻辑。不要让模型输出一大段自然语言后再反向解析。

错误方式：

```text
用户输入 → DeepSeek 直接输出完整行程文本 → 后端尝试解析
```

正确方式：

```text
用户输入 → DeepSeek 输出结构化意图 JSON → 后端检索 POI / 调高德 / 算路线 → DeepSeek 解释路线
```

### 3.2 DeepSeek 不负责事实性地理计算

DeepSeek 不直接输出真实路线时间、真实距离、真实天气、真实经纬度。这些必须来自：

1. 本地 POI 数据库；
2. 高德 Web 服务 API；
3. 后端行程规划算法。

### 3.3 Prompt 输出必须可校验

每个 Prompt 对应一个 Pydantic Schema。后端收到模型输出后，必须进行：

1. JSON 解析；
2. Schema 校验；
3. 默认值补齐；
4. 异常重试；
5. 失败兜底。

---

## 4. 用户意图解析 Prompt

### 4.1 文件

```text
backend/app/prompts/intent_parser.md
```

### 4.2 输入示例

```text
我想去重庆玩3天，预算2500，喜欢美食、拍照和夜景，不想太累，尽量坐地铁。
```

### 4.3 输出 JSON Schema 语义

```json
{
  "destination": "重庆",
  "days": 3,
  "budget": 2500,
  "preferences": ["美食", "拍照", "夜景"],
  "avoid": ["高强度路线"],
  "travel_style": "relaxed",
  "walking_tolerance": "medium",
  "transport_preference": "public_transport",
  "need_hotel_area": true,
  "need_weather_adjustment": true,
  "has_imported_note": false,
  "missing_fields": [],
  "clarifying_question": ""
}
```

### 4.4 枚举约束

`travel_style`：

```text
relaxed / standard / intensive
```

`walking_tolerance`：

```text
low / medium / high
```

`transport_preference`：

```text
walk / public_transport / taxi / drive / mixed
```

### 4.5 缺失字段处理

如果用户没有提供预算，输出：

```json
{
  "budget": null,
  "missing_fields": ["budget"],
  "clarifying_question": "请补充本次旅行的人均预算，或者允许系统使用中等预算默认值。"
}
```

---

## 5. 攻略文本抽取 Prompt

### 5.1 文件

```text
backend/app/prompts/note_extractor.md
```

### 5.2 输入示例

```text
重庆三日游：第一天解放碑、八一好吃街、洪崖洞，晚上去千厮门大桥拍照。第二天山城步道、十八梯、白象居。第三天鹅岭二厂、李子坝、观音桥。
```

### 5.3 输出示例

```json
{
  "city": "重庆",
  "pois": [
    {
      "raw_name": "解放碑",
      "normalized_name": "解放碑",
      "poi_type": "商圈",
      "tags": ["经典打卡", "商圈", "美食"],
      "recommended_time": "全天",
      "suggested_duration_minutes": 90,
      "tips": [],
      "confidence": 0.9
    }
  ],
  "global_tips": ["节假日洪崖洞人流较大"],
  "detected_days": 3
}
```

### 5.4 抽取边界

只抽取可用于路线规划的地点，不抽取：

1. 人名；
2. 博主名；
3. 账号；
4. 电话；
5. 过于笼统的形容词；
6. 不明确的“这里”“那边”。

---

## 6. 行程解释 Prompt

### 6.1 文件

```text
backend/app/prompts/itinerary_explainer.md
```

### 6.2 输入

后端已经生成的结构化行程，例如：

```json
{
  "plan_type": "少走路轻松方案",
  "destination": "重庆",
  "days": [
    {
      "day_index": 1,
      "items": [
        {"poi_name": "解放碑", "start_time": "09:30", "end_time": "11:00"},
        {"poi_name": "八一好吃街", "start_time": "11:30", "end_time": "12:30"}
      ]
    }
  ]
}
```

### 6.3 输出

```json
{
  "summary": "这套方案以解放碑片区为第一天核心，减少跨区移动，适合第一次来重庆且不想太累的用户。",
  "daily_explanations": [
    {
      "day_index": 1,
      "explanation": "第一天集中在解放碑及周边，步行和短距离交通即可覆盖多个经典点位。",
      "tips": ["洪崖洞建议晚上远景拍摄", "八一好吃街饭点排队较多"]
    }
  ],
  "pros": ["点位集中", "交通压力低"],
  "cons": ["覆盖范围不如高强度方案广"],
  "suitable_for": ["第一次来重庆", "轻松游用户", "拍照用户"]
}
```

---

## 7. 路线调整 Prompt

### 7.1 文件

```text
backend/app/prompts/route_adjuster.md
```

### 7.2 输入示例

```text
我不想去洪崖洞，人太多了，能不能少走路，多安排点美食？
```

### 7.3 输出示例

```json
{
  "actions": [
    {
      "action_type": "remove_poi",
      "target_poi": "洪崖洞",
      "reason": "用户明确表示不想去"
    },
    {
      "action_type": "decrease_walking",
      "target_poi": "",
      "reason": "用户希望少走路"
    },
    {
      "action_type": "increase_preference",
      "target_preference": "美食",
      "reason": "用户希望增加美食点"
    }
  ],
  "priority": "hard_constraint",
  "need_regenerate": true,
  "user_message": "已理解你的调整要求：删除洪崖洞，降低步行强度，并增加美食点位权重。"
}
```

---

## 8. 工具调用决策 Prompt

### 8.1 文件

```text
backend/app/prompts/tool_decision.md
```

### 8.2 作用

该 Prompt 不直接调用工具，只判断下一步需要调用哪些后端工具。例如：

1. `search_poi`；
2. `calculate_route`；
3. `query_weather`；
4. `generate_itinerary`；
5. `explain_itinerary`。

### 8.3 输出示例

```json
{
  "tool_calls": [
    {
      "tool_name": "search_poi",
      "arguments": {
        "city": "重庆",
        "keywords": ["洪崖洞", "解放碑"]
      },
      "reason": "需要确认用户攻略中的地点是否存在真实 POI"
    },
    {
      "tool_name": "query_weather",
      "arguments": {
        "city": "重庆"
      },
      "reason": "用户需要雨天路线调整"
    }
  ]
}
```

---

## 9. 后端失败处理

### 9.1 JSON 解析失败

处理流程：

```text
第一次请求失败
  ↓
重新请求一次，并要求“只输出合法 json”
  ↓
仍失败则返回默认结构
  ↓
记录日志
```

### 9.2 JSON 字段缺失

处理流程：

```text
Pydantic 校验失败
  ↓
用默认值补齐非核心字段
  ↓
核心字段缺失则返回 clarifying_question
```

核心字段包括：

```text
destination
days
```

预算可以为空，但需要后续提示用户或使用默认预算。

### 9.3 DeepSeek 返回空 content

处理流程：

```text
空 content
  ↓
自动重试一次
  ↓
仍为空则使用默认兜底输出
```

---

## 10. 第五步完成标准

第五步完成时，项目应满足：

```text
1. docs/PROMPT_DESIGN.md 已完成
2. backend/app/prompts/ 下已有 5 个 Prompt 文件
3. backend/app/schemas/llm_schema.py 已定义结构化输出 Schema
4. backend/app/services/deepseek_service.py 可以读取 Prompt 并请求 DeepSeek
5. backend/tools/test_prompt_intent_parser.py 可以解析用户旅行需求
6. backend/tools/test_prompt_note_extractor.py 可以抽取攻略 POI
7. backend/tools/test_prompt_route_adjuster.py 可以解析调整指令
```
