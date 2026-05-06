# 旅渡 TravelDu V1 数据库设计文档

## 1. 设计目标

旅渡 V1 的数据库用于支撑“用户输入旅行需求或导入攻略文本后，系统生成多套可执行本地旅行路线”的核心闭环。

V1 数据库设计遵循以下原则：

1. 先满足单城市、单人规划、网页端 MVP；
2. 以 SQLite 作为开发环境默认数据库，后续可平滑迁移 PostgreSQL；
3. 不把 DeepSeek 的自然语言输出直接作为业务数据存储，必须先结构化；
4. POI 数据以本地种子知识库为主，高德返回信息作为地理校准数据；
5. 行程数据采用“行程任务 → 多套方案 → 每日路线 → 路线点位”的层级结构；
6. API 调用必须记录日志，便于调试 DeepSeek 和高德接口；
7. V1 暂不设计支付、订单、社区、实时多人协同和复杂用户体系。

---

## 2. 数据库选择

### 2.1 开发阶段

开发阶段使用 SQLite：

```text
backend/storage/traveldu_v1.db
```

优点：

1. 启动成本低；
2. 无需单独安装数据库服务；
3. 适合本地 MVP 验证；
4. 便于直接查看和备份。

### 2.2 后续阶段

V1 稳定后可迁移到 PostgreSQL。迁移时重点调整：

1. JSON 字段类型；
2. 索引；
3. 并发写入；
4. 地理空间扩展 PostGIS。

V1 不直接使用 PostGIS，路线和距离计算由高德 API 提供。

---

## 3. 核心实体关系

```text
users
  └── user_profiles

pois
  └── content_knowledge

users
  └── guide_imports
        └── guide_extracted_pois

users
  └── itineraries
        └── itinerary_plans
              └── daily_routes
                    └── route_items
                          └── pois

api_call_logs
```

核心行程结构：

```text
一次用户规划请求 = itineraries
一套候选方案 = itinerary_plans
某一天路线 = daily_routes
当天的具体点位 = route_items
具体地点信息 = pois
```

---

## 4. 表结构设计

## 4.1 用户表：users

### 用途

保存轻量用户信息。V1 可以使用游客模式，不强制登录。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| session_id | VARCHAR(128) | 是 | 游客会话 ID |
| nickname | VARCHAR(64) | 否 | 用户昵称 |
| email | VARCHAR(128) | 否 | 邮箱，V1 可为空 |
| phone | VARCHAR(32) | 否 | 手机号，V1 可为空 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

### 索引

```text
idx_users_session_id
```

---

## 4.2 用户画像表：user_profiles

### 用途

保存用户在一次或多次规划中的偏好信息。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| user_id | INTEGER | 是 | 关联 users.id |
| destination | VARCHAR(64) | 是 | 目的地城市 |
| days | INTEGER | 是 | 出行天数 |
| budget | INTEGER | 否 | 预算上限，单位元 |
| travel_style | VARCHAR(32) | 是 | relaxed / standard / intensive |
| walking_tolerance | VARCHAR(32) | 是 | low / medium / high |
| transport_preference | VARCHAR(32) | 是 | public_transport / taxi / walking / mixed |
| preferences | JSON | 否 | 偏好标签数组 |
| avoid_preferences | JSON | 否 | 不喜欢或规避项 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

### 说明

`preferences` 示例：

```json
["美食", "拍照", "夜景"]
```

`avoid_preferences` 示例：

```json
["高强度路线", "长时间排队"]
```

---

## 4.3 POI 表：pois

### 用途

保存本地旅行知识库中的地点信息，以及高德匹配后的真实地理信息。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| poi_name | VARCHAR(128) | 是 | 本地标准 POI 名称 |
| poi_alias | VARCHAR(256) | 否 | 别名 |
| city | VARCHAR(64) | 是 | 城市 |
| district | VARCHAR(64) | 否 | 行政区 |
| poi_type | VARCHAR(64) | 是 | POI 类型 |
| tags | JSON | 否 | 标签数组 |
| recommended_duration_minutes | INTEGER | 是 | 建议停留时间 |
| best_time | VARCHAR(128) | 否 | 推荐时间段 |
| avoid_time | VARCHAR(128) | 否 | 不建议时间段 |
| price_level | VARCHAR(32) | 是 | free / low / medium / high |
| estimated_cost_low | INTEGER | 是 | 估算最低消费 |
| estimated_cost_high | INTEGER | 是 | 估算最高消费 |
| indoor_outdoor | VARCHAR(32) | 是 | indoor / outdoor / mixed |
| suitable_for | JSON | 否 | 适合人群 |
| avoid_tips | TEXT | 否 | 避坑提示 |
| nearby_area | VARCHAR(128) | 否 | 片区分组 |
| amap_poi_id | VARCHAR(128) | 否 | 高德 POI ID |
| longitude | FLOAT | 否 | 经度 |
| latitude | FLOAT | 否 | 纬度 |
| amap_name | VARCHAR(128) | 否 | 高德返回名称 |
| amap_address | VARCHAR(256) | 否 | 高德返回地址 |
| amap_type | VARCHAR(256) | 否 | 高德返回类型 |
| amap_cityname | VARCHAR(64) | 否 | 高德返回城市 |
| amap_adname | VARCHAR(64) | 否 | 高德返回区县 |
| match_score | INTEGER | 否 | 高德匹配得分 |
| match_status | VARCHAR(32) | 是 | matched / manual_verified / low_confidence / not_found |
| match_keyword | VARCHAR(128) | 否 | 实际匹配关键词 |
| source | VARCHAR(32) | 是 | manual / user_paste / amap / authorized |
| confidence | FLOAT | 是 | 本地数据可信度 |
| is_active | BOOLEAN | 是 | 是否启用 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

### 索引

```text
idx_pois_city
idx_pois_city_type
idx_pois_nearby_area
idx_pois_amap_poi_id
```

### 说明

V1 中 `matched` 和 `manual_verified` 可进入正式规划候选池；`low_confidence` 默认不进入正式规划，除非人工确认。

---

## 4.4 内容知识表：content_knowledge

### 用途

保存从攻略文本、人工整理或授权内容中抽取出的旅行知识。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| poi_id | INTEGER | 否 | 关联 pois.id，可为空 |
| city | VARCHAR(64) | 是 | 城市 |
| source_type | VARCHAR(32) | 是 | manual / user_paste / xhs_authorized / other |
| raw_text_hash | VARCHAR(128) | 否 | 原始文本哈希 |
| summary | TEXT | 否 | 内容摘要 |
| positive_tags | JSON | 否 | 正向标签 |
| negative_tips | JSON | 否 | 避坑点 |
| recommended_time | VARCHAR(128) | 否 | 推荐时间 |
| suggested_duration_minutes | INTEGER | 否 | 建议停留时间 |
| heat_score | FLOAT | 否 | 热度分，V1 可人工设定 |
| confidence | FLOAT | 是 | 可信度 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.5 攻略导入表：guide_imports

### 用途

记录用户主动粘贴的攻略文本。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| user_id | INTEGER | 否 | 关联 users.id，游客可为空 |
| destination | VARCHAR(64) | 否 | 目标城市 |
| raw_text | TEXT | 是 | 用户粘贴的攻略文本 |
| raw_text_hash | VARCHAR(128) | 是 | 文本哈希，用于去重 |
| extract_status | VARCHAR(32) | 是 | pending / success / failed |
| error_message | TEXT | 否 | 抽取失败原因 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.6 攻略抽取地点表：guide_extracted_pois

### 用途

保存 DeepSeek 从攻略文本中抽取出的地点与建议。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| guide_import_id | INTEGER | 是 | 关联 guide_imports.id |
| raw_name | VARCHAR(128) | 是 | 攻略中出现的原始地点名 |
| normalized_name | VARCHAR(128) | 否 | 归一化地点名 |
| poi_id | INTEGER | 否 | 匹配到的 pois.id |
| amap_poi_id | VARCHAR(128) | 否 | 匹配到的高德 POI ID |
| poi_type | VARCHAR(64) | 否 | 类型 |
| tags | JSON | 否 | 标签 |
| recommended_time | VARCHAR(128) | 否 | 推荐时间 |
| suggested_duration_minutes | INTEGER | 否 | 建议停留时间 |
| tips | JSON | 否 | 攻略中的提醒或避坑 |
| match_status | VARCHAR(32) | 是 | pending / matched / need_user_confirm / ignored |
| user_confirmed | BOOLEAN | 是 | 用户是否确认加入规划 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.7 行程任务表：itineraries

### 用途

保存一次用户发起的行程规划任务。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| user_id | INTEGER | 否 | 关联 users.id |
| guide_import_id | INTEGER | 否 | 如果由攻略导入触发，则关联 guide_imports.id |
| destination | VARCHAR(64) | 是 | 目的地 |
| days | INTEGER | 是 | 天数 |
| budget | INTEGER | 否 | 预算 |
| preferences | JSON | 否 | 偏好 |
| avoid_preferences | JSON | 否 | 规避项 |
| travel_style | VARCHAR(32) | 是 | relaxed / standard / intensive |
| walking_tolerance | VARCHAR(32) | 是 | low / medium / high |
| transport_preference | VARCHAR(32) | 是 | 交通偏好 |
| raw_user_input | TEXT | 否 | 用户原始输入 |
| parsed_intent | JSON | 否 | DeepSeek 解析出的结构化意图 |
| status | VARCHAR(32) | 是 | pending / success / failed |
| error_message | TEXT | 否 | 失败原因 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.8 行程方案表：itinerary_plans

### 用途

保存一次行程任务下的多套方案。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| itinerary_id | INTEGER | 是 | 关联 itineraries.id |
| plan_type | VARCHAR(64) | 是 | comprehensive / low_budget / relaxed / food_experience / classic |
| title | VARCHAR(128) | 是 | 方案标题 |
| summary | TEXT | 否 | 方案摘要 |
| suitable_for | JSON | 否 | 适合人群 |
| advantages | JSON | 否 | 优点 |
| disadvantages | JSON | 否 | 缺点 |
| total_estimated_cost_low | INTEGER | 是 | 总预算下限 |
| total_estimated_cost_high | INTEGER | 是 | 总预算上限 |
| total_transport_time_minutes | INTEGER | 是 | 总交通时间 |
| total_walking_distance_meters | INTEGER | 是 | 总步行距离 |
| score | FLOAT | 否 | 方案综合得分 |
| is_selected | BOOLEAN | 是 | 用户是否选择该方案 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.9 每日路线表：daily_routes

### 用途

保存某一套方案中的某一天路线。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| plan_id | INTEGER | 是 | 关联 itinerary_plans.id |
| day_index | INTEGER | 是 | 第几天，从 1 开始 |
| title | VARCHAR(128) | 否 | 当天标题 |
| summary | TEXT | 否 | 当天摘要 |
| estimated_cost_low | INTEGER | 是 | 当天预算下限 |
| estimated_cost_high | INTEGER | 是 | 当天预算上限 |
| estimated_transport_time_minutes | INTEGER | 是 | 当天交通时间 |
| estimated_walking_distance_meters | INTEGER | 是 | 当天步行距离 |
| weather_summary | VARCHAR(256) | 否 | 天气摘要 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.10 路线点位表：route_items

### 用途

保存每日路线中的具体点位和点位之间的交通信息。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| daily_route_id | INTEGER | 是 | 关联 daily_routes.id |
| poi_id | INTEGER | 是 | 关联 pois.id |
| sort_order | INTEGER | 是 | 当天路线顺序 |
| start_time | VARCHAR(16) | 否 | 建议开始时间，例如 09:30 |
| end_time | VARCHAR(16) | 否 | 建议结束时间，例如 11:00 |
| duration_minutes | INTEGER | 是 | 停留时间 |
| transport_to_next | VARCHAR(32) | 否 | 到下一个点的交通方式 |
| distance_to_next_meters | INTEGER | 否 | 到下一个点距离 |
| time_to_next_minutes | INTEGER | 否 | 到下一个点预计时间 |
| route_polyline_to_next | TEXT | 否 | 到下一个点的地图折线 |
| reason | TEXT | 否 | 为什么安排该点 |
| tips | TEXT | 否 | 点位提示 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 4.11 API 调用日志表：api_call_logs

### 用途

记录 DeepSeek、高德等外部服务调用情况，用于调试、成本估算和异常追踪。

### 字段

| 字段名 | 类型 | 是否必填 | 说明 |
|---|---|---:|---|
| id | INTEGER | 是 | 主键 |
| provider | VARCHAR(32) | 是 | deepseek / amap |
| api_name | VARCHAR(64) | 是 | 接口名称 |
| request_hash | VARCHAR(128) | 否 | 请求哈希 |
| request_summary | TEXT | 否 | 请求摘要，不能保存 API Key |
| response_summary | TEXT | 否 | 响应摘要 |
| status | VARCHAR(32) | 是 | success / failed |
| latency_ms | INTEGER | 否 | 延迟毫秒 |
| error_message | TEXT | 否 | 错误信息 |
| created_at | DATETIME | 是 | 创建时间 |

### 安全要求

不得保存：

1. DeepSeek API Key；
2. 高德 API Key；
3. 用户精确实时轨迹；
4. 用户敏感隐私文本。

---

## 5. 枚举值约定

### 5.1 travel_style

```text
relaxed      轻松游
standard     标准游
intensive    高强度打卡游
```

### 5.2 walking_tolerance

```text
low       不想多走路
medium    正常步行
high      可接受高强度步行
```

### 5.3 transport_preference

```text
public_transport
walking
taxi
mixed
```

### 5.4 plan_type

```text
comprehensive       综合最优方案
low_budget          低预算方案
relaxed             少走路轻松方案
food_experience     美食体验方案
classic             经典打卡方案
```

### 5.5 match_status

```text
matched             高德自动匹配成功
manual_verified     人工确认匹配成功
need_review         需要人工确认
low_confidence      低置信度
not_found           未找到
```

---

## 6. V1 查询场景

### 6.1 查询某城市可用 POI

```sql
SELECT * FROM pois
WHERE city = '重庆'
  AND is_active = 1
  AND match_status IN ('matched', 'manual_verified');
```

### 6.2 查询某片区 POI

```sql
SELECT * FROM pois
WHERE city = '重庆'
  AND nearby_area = '解放碑片区'
  AND is_active = 1;
```

### 6.3 查询某个行程下的所有方案

```sql
SELECT * FROM itinerary_plans
WHERE itinerary_id = :itinerary_id
ORDER BY score DESC;
```

### 6.4 查询某套方案的完整路线

```sql
SELECT
  dr.day_index,
  ri.sort_order,
  p.poi_name,
  ri.start_time,
  ri.end_time,
  ri.duration_minutes,
  ri.transport_to_next,
  ri.time_to_next_minutes
FROM daily_routes dr
JOIN route_items ri ON dr.id = ri.daily_route_id
JOIN pois p ON ri.poi_id = p.id
WHERE dr.plan_id = :plan_id
ORDER BY dr.day_index, ri.sort_order;
```

---

## 7. 开发阶段数据库文件位置

建议：

```text
backend/storage/traveldu_v1.db
```

不要上传正式数据库文件到 GitHub。

`.gitignore` 中应加入：

```text
.env
*.db
backend/storage/
```

---

## 8. 当前阶段完成标准

第四步完成时应具备：

1. `docs/DB_DESIGN.md` 已创建；
2. SQLAlchemy 数据库连接文件已创建；
3. SQLAlchemy 模型文件已创建；
4. 可以执行初始化脚本创建 SQLite 数据库；
5. 可以执行 POI 导入脚本，把 `data/processed/chongqing_pois_enriched.csv` 导入 `pois` 表；
6. 可以用查询脚本确认 POI 数量为 30。
