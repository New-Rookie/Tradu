# Itinerary Adjustment Design

## itinerary_state
itinerary_states 保存 session_id、itinerary_id、预算、偏好、avoid、walking_tolerance、transport_preference、hotel_area、locked/removed/confirmed/replaced_pois、weather_mode、current_location、latest_itinerary_payload 和 adjustment_history。

## 用户调整动作
支持 remove_poi、replace_poi、reduce_walking、increase_preference、decrease_budget、rain_mode、compress_day、continue_from_current_location、change_transport_preference。

## 一键减少步行
将 walking_tolerance 设置为 low，减少每日点位数量，提高同片区权重，降低跨区移动，交通方式偏公共交通/打车。

## 雨天模式
weather_mode=rainy，提高 indoor/mixed、博物馆、商圈、餐饮权重，降低 outdoor/citywalk，并在解释中说明天气影响。

## 删除点位
removed_pois 是硬约束。用户删除过的 POI 后续所有方案不得再出现，锁定点位不应被自动删除。

## 压缩半天
compress_day 保留 2-3 个最高价值点和餐饮/休息，控制在 4-5 小时，减少跨区。

## 从当前位置继续规划
current_location 作为当天剩余路线起点，重新排序附近点位，不返回已过时或用户跳过点位。
