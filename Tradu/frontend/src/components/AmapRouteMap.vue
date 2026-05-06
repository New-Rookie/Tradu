<template>
  <div class="map-shell">
    <div ref="mapRef" class="map-container"></div>
    <div class="map-panel" v-if="day">
      <div class="panel-title">{{ day.title }}</div>
      <div class="panel-meta">
        {{ day.items?.length || 0 }} 个点位 · 步行约 {{ day.walking_distance_km || 0 }} km · 交通约 {{ day.transport_time_minutes || 0 }} 分钟
      </div>
      <div class="legend"><span>景点</span><span>餐饮</span><span>住宿区域</span><span>休息</span></div>
      <ol class="poi-list">
        <li v-for="item in day.items" :key="itemKey(item)">
          <strong>{{ item.poi_name }}</strong>
          <span>{{ item.item_type === "meal" ? "餐饮" : item.poi_type || 'POI' }}</span>
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";
import type { DailyRoute, RouteItem } from "../stores/itineraryStore";
import type { HotelAreaRecommendation } from "../api/types";

const props = defineProps<{
  day: DailyRoute | null;
  hotelArea?: HotelAreaRecommendation | null;
}>();

const mapRef = ref<HTMLDivElement | null>(null);
let AMapInstance: any = null;
let map: any = null;
let overlays: any[] = [];

function itemKey(item: RouteItem) {
  return `${item.poi_id ?? item.poi_name}-${item.longitude}-${item.latitude}-${item.sort_order}`;
}

function validItems(day: DailyRoute | null): RouteItem[] {
  return (day?.items || []).filter((item) => {
    return typeof item.longitude === "number" && typeof item.latitude === "number";
  });
}

async function initMap() {
  if (!mapRef.value || map) return;

  const securityJsCode = import.meta.env.VITE_AMAP_JS_SECURITY_JSCODE;
  const apiKey = import.meta.env.VITE_AMAP_JS_API_KEY;

  if (!apiKey || !securityJsCode) {
    console.error("Missing AMap JS API env variables.");
    return;
  }

  (window as any)._AMapSecurityConfig = {
    securityJsCode,
  };

  AMapInstance = await AMapLoader.load({
    key: apiKey,
    version: "2.0",
    plugins: ["AMap.Scale", "AMap.ToolBar"],
  });

  map = new AMapInstance.Map(mapRef.value, {
    zoom: 12,
    center: [106.551556, 29.563009],
    viewMode: "2D",
  });

  map.addControl(new AMapInstance.Scale());
  map.addControl(new AMapInstance.ToolBar());

  drawRoute();
}

function clearOverlays() {
  if (!map || overlays.length === 0) return;
  map.remove(overlays);
  overlays = [];
}

function markerContent(item: RouteItem, index: number) {
  const color = item.item_type === "meal" ? "#f79009" : item.item_type === "rest" ? "#12b76a" : "#315efb";
  return `<div style="background:${color};color:white;border-radius:999px;padding:5px 8px;font-weight:800;border:2px solid white;box-shadow:0 6px 16px rgba(0,0,0,.2)">${index}</div>`;
}

function hotelAreaMarker() {
  if (!map || !AMapInstance || !props.hotelArea?.longitude || !props.hotelArea?.latitude) return null;
  return new AMapInstance.Marker({
    position: [props.hotelArea.longitude, props.hotelArea.latitude],
    title: props.hotelArea.area_name,
    content: `<div style="background:#7a5af8;color:white;border-radius:8px;padding:6px 8px;font-weight:800;border:2px solid white">住</div>`,
    offset: new AMapInstance.Pixel(-13, -30),
  });
}

function drawRoute() {
  if (!map || !AMapInstance) return;
  clearOverlays();

  const items = validItems(props.day);
  if (!items.length) return;

  const markers = items.map((item, index) => {
    const marker = new AMapInstance.Marker({
      position: [item.longitude, item.latitude],
      title: item.poi_name,
      content: markerContent(item, index + 1),
      offset: new AMapInstance.Pixel(-13, -30),
    });

    marker.on("click", () => {
      const info = new AMapInstance.InfoWindow({
        content: `
          <div style="padding:8px 10px;line-height:1.6;min-width:180px">
            <div style="font-weight:700;margin-bottom:4px">${index + 1}. ${item.poi_name}</div>
            <div>类型：${item.item_type === "meal" ? "餐饮" : item.poi_type || "-"}</div>
            <div>片区：${item.nearby_area || "-"}</div>
            <div>停留：${item.suggested_duration_minutes || 0} 分钟</div>
            <div>预算：${item.estimated_cost_low || 0}-${item.estimated_cost_high || 0}</div>
            <div>理由：${item.reason || "-"}</div>
            <div>提示：${item.tips || "暂无"}</div>
            <div>下一站：${item.transport_to_next || "-"}</div>
          </div>
        `,
      });
      info.open(map, marker.getPosition());
    });

    return marker;
  });

  const path = items.map((item) => [item.longitude, item.latitude]);
  const polyline = new AMapInstance.Polyline({
    path,
    strokeWeight: 6,
    strokeOpacity: 0.85,
    lineJoin: "round",
    lineCap: "round",
  });

  const hotelMarker = hotelAreaMarker();
  overlays = hotelMarker ? [...markers, hotelMarker, polyline] : [...markers, polyline];
  map.add(overlays);
  map.setFitView(overlays, false, [80, 80, 80, 80]);
}

onMounted(async () => {
  await initMap();
});

watch(
  () => [props.day, props.hotelArea],
  () => drawRoute(),
  { deep: true }
);

onBeforeUnmount(() => {
  clearOverlays();
  if (map) {
    map.destroy();
    map = null;
  }
});
</script>

<style scoped>
.map-shell {
  position: relative;
  width: 100%;
  min-height: 680px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid #e4e7ec;
  background: #f6f8fb;
}

.map-container {
  width: 100%;
  height: 680px;
}

.map-panel {
  position: absolute;
  left: 18px;
  top: 18px;
  width: 320px;
  max-height: 620px;
  overflow: auto;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #e4e7ec;
  box-shadow: 0 16px 40px rgba(16, 24, 40, 0.12);
  border-radius: 16px;
  padding: 16px;
}

.panel-title {
  font-weight: 800;
  color: #172033;
  font-size: 16px;
}

.panel-meta {
  margin-top: 6px;
  color: #667085;
  font-size: 12px;
}

.poi-list {
  margin: 14px 0 0;
  padding-left: 18px;
}

.poi-list li {
  margin-bottom: 10px;
  color: #172033;
}

.poi-list span {
  margin-left: 8px;
  color: #667085;
  font-size: 12px;
}
</style>

<style scoped>
.legend { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.legend span { border-radius: 999px; background: #eef3ff; color: #315efb; padding: 4px 8px; font-size: 12px; }
</style>
