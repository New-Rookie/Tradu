# 旅渡 V1 行程评分与路线生成算法设计

## 1. 设计目标

第八步的目标是将行程生成逻辑从“按 POI 顺序拼接”升级为“可解释、可调参、可扩展”的规则评分算法。

V1 不使用复杂机器学习模型，原因如下：

1. 当前 POI 数据规模较小，规则评分足够；
2. 用户输入约束明确，主要是偏好、预算、天数和体力；
3. 旅行路线需要可解释，而黑盒推荐不利于排查问题；
4. V1 需要快速形成可运行闭环。

因此采用：

```text
POI 打分 → 片区聚类 → 每日点位选择 → 日内排序 → 预算/距离估算 → 多方案输出
```

---

## 2. 输入数据

算法输入包括三类。

### 2.1 用户需求

```json
{
  "destination": "重庆",
  "days": 3,
  "budget": 2500,
  "preferences": ["美食", "拍照", "夜景"],
  "avoid": ["高强度路线"],
  "travel_style": "relaxed",
  "walking_tolerance": "medium",
  "transport_preference": "public_transport"
}
```

### 2.2 POI 数据

来自数据库 `pois` 表，关键字段包括：

```text
poi_name
city
district
poi_type
tags
recommended_duration_minutes
best_time
price_level
estimated_cost_low
estimated_cost_high
indoor_outdoor
nearby_area
longitude
latitude
confidence
match_status
```

### 2.3 天气数据

V1 只使用城市级天气信息。

```json
{
  "weather": "阴",
  "temperature": "30"
}
```

---

## 3. POI 评分公式

基础评分由 6 个子分数组成：

```text
Score(poi) =
  w_pref    × preference_score
+ w_geo     × geo_score
+ w_budget  × budget_score
+ w_content × content_score
+ w_time    × time_score
+ w_weather × weather_score
```

不同方案类型使用不同权重。

---

## 4. 五套方案策略

### 4.1 综合最优方案

权重均衡，优先生成适合多数用户的路线。

### 4.2 低预算方案

提高预算适配权重，优先选择免费和低消费点位。

### 4.3 少走路轻松方案

提高地理便利性权重，减少跨片区移动，每日点位数量偏少。

### 4.4 美食体验方案

提高餐饮、美食、夜市、商圈类点位权重。

### 4.5 经典打卡方案

提高经典打卡、地标、夜景、热门拍照点权重。

---

## 5. 每日点位数量规则

```text
relaxed：每天 3—4 个点位
standard：每天 4—5 个点位
intensive：每天 5—6 个点位
```

不同方案会在此基础上微调。例如“少走路轻松方案”会减少 1 个点位，“经典打卡方案”可增加 1 个点位。

---

## 6. 片区聚类规则

路线规划优先遵循片区聚类：

1. 同一天优先安排同一片区或相邻片区；
2. 每天选择 1 个主片区，最多补充 1 个临近片区；
3. 避免一天内频繁跨区；
4. 如果用户天数较多，按片区分摊不同天。

当前 V1 不维护复杂的片区邻接图，而是使用 POI 坐标中心点之间的距离估算片区接近程度。

---

## 7. 日内排序规则

日内排序遵循：

```text
上午适合点 → 餐饮/商圈 → 下午适合点 → 夜景/商圈
```

如果同一时间段多个点位，则用最近邻方式进行排序，减少折返。

---

## 8. 天气影响规则

```text
下雨：降低 outdoor、citywalk、自然景观权重，提高 indoor、博物馆、商圈、餐饮权重
高温：降低中午户外点位权重
低温：降低夜间户外点位权重
```

---

## 9. 输出结构

后端输出前端可直接展示的结构：

```json
{
  "itinerary_id": "formal_xxx",
  "destination": "重庆",
  "plans": [
    {
      "plan_type": "综合最优方案",
      "title": "重庆3日综合最优方案",
      "summary": "...",
      "score": 83.4,
      "total_estimated_cost_low": 260,
      "total_estimated_cost_high": 720,
      "total_transport_distance_km": 18.6,
      "total_transport_time_minutes": 95,
      "days": [
        {
          "day_index": 1,
          "title": "Day 1 解放碑片区",
          "summary": "...",
          "items": []
        }
      ]
    }
  ]
}
```

---

## 10. 后续扩展

第八步之后可继续增强：

1. 使用高德路线规划 API 替换直线距离近似；
2. 为地图页输出 Polyline；
3. 加入用户反馈分；
4. 加入景点开放时间；
5. 加入酒店区域推荐；
6. 扩展到成都、杭州、上海等城市。
