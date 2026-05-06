# Tradu V1 Development Plan

## 当前 MVP 状态
已具备 FastAPI + Vue 3 架构、本地重庆 attraction POI、DeepSeek/高德基础接口、5 套路线生成和地图 Marker/Polyline 展示。

## V1 目标
产品定位升级为“预算约束下的 AI 本地旅行路线执行助手”。输入城市、天数、预算、偏好后，输出 5 套包含住宿区域、午晚餐、预算明细、交通与步行估算的可执行路线。

## 新增模块
- service_pois：缓存高德酒店、餐饮、商圈、休息点等服务型 POI。
- hotel_areas：推荐住宿区域，不做酒店预订。
- itinerary_states：保存会话路线状态，支持删除点位、少走路、雨天、压缩半天、当前位置继续。
- user_sessions / chat_messages：保存游客会话与对话结构化结果。
- BudgetPlanner / MealPlanner / HotelAreaService / AMapServicePoiFetcher / ItineraryAdjustmentService。

## 数据来源策略
V1 只使用本地 POI、高德 Web 服务/周边搜索/天气/距离、高德 JS API、用户输入、攻略粘贴文本和 DeepSeek 结构化理解。

## 不做范围
不做机票/火车/酒店/餐厅/门票交易，不做支付，不做小红书/携程/美团/去哪儿爬虫，不承诺实时库存和实时价格。

## 开发顺序
按 poi_id 修复、service_pois、高德服务 POI、预算、住宿区域、餐饮、行程生成增强、itinerary_state、调整服务、API、前端、测试、文档推进。

## 验收标准
重庆 3 天 2500 元美食/拍照/夜景/不太累请求能生成 5 套方案；每套含住宿区域、每日景点、午晚餐、预算、交通、步行、理由、风险；支持少走路、雨天、删除洪崖洞、自然语言调整并保存 itinerary_state。
