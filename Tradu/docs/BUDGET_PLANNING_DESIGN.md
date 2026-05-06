# Budget Planning Design

预算功能是“预算约束估算”，不承诺绝对准确价格。

## 拆分模型
总预算 = 住宿预算 + 餐饮预算 + 景点预算 + 市内交通预算 + 机动预算。默认保留 10%-15% 以上机动空间。

## 住宿预算
V1 推荐住宿区域而非具体酒店预订。低预算优先 low/medium 区域，高预算可接受核心热门区。

## 餐饮预算
按天拆分 daily_food_budget。低预算优先 low/unknown 餐饮或餐饮区域，中高预算提高评分与体验弹性。

## 景点预算
使用本地 POI estimated_cost_low/high 与 price_level。低预算提高 free/low 点位权重，降低 high 消费点位。

## 交通预算
结合交通偏好和跨区距离估算。少走路或轻松游提高公共交通/打车衔接权重，减少跨区。

## Buffer
buffer_budget 用于节假日涨价、临时打车、排队换点等不确定性。

## 风险提示
输出 budget_tight、budget_normal、budget_flexible，以及路线估算可能超预算、buffer 过低等提示。
