# AMap Data Strategy

## 为什么 V1 只用高德
高德能覆盖 POI、经纬度、周边搜索、天气、路线距离与 JS 地图展示，足以支撑 V1 本地旅行路线执行助手；同时避免多平台爬虫与交易复杂度。

## 用于哪些数据
- attraction POI 坐标与高德 POI ID 补全；
- service_pois 中酒店、餐饮、商圈、休息点候选；
- 天气模式；
- 路线距离/时间估算；
- 前端地图 Marker 和 Polyline。

## 限制
高德 cost/rating 可能缺失或波动，POI 分类不保证完全准确。V1 必须保留 unknown price_level，前端不返回 raw_payload。

## 缓存策略
service_pois 按 city + service_type + nearby_area 缓存，默认 3 天过期；行程生成优先查缓存，不每次强制刷新。

## service_pois 设计
包含 amap_poi_id、name、city、district、nearby_area、坐标、service_type、poi_type、tags、rating、cost、price_level、business_area、source、raw_payload 和更新时间。

## 后续扩展
未来可在合规前提下接入官方开放平台或人工维护数据源，但 V1 不接入小红书、携程、美团、去哪儿爬虫。
