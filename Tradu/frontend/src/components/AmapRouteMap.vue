<template>
  <div class="map-shell">
    <div ref="mapRef" class="map-container"></div>
    <div class="map-panel" v-if="day">
      <div class="panel-title">{{ day.title }}</div>
      <div class="panel-meta">
        {{ day.items?.length || 0 }} 个点位 · 步行约 {{ day.walking_distance_km || 0 }} km · 交通约 {{ day.transport_time_minutes || 0 }} 分钟
      </div>
      <ol class="poi-list">
        <li v-for="item in day.items" :key="itemKey(item)">
          <strong>{{ item.poi_name }}</strong>
          <span>{{ item.poi_type || 'POI' }}</span>
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";
import type { DailyRoute, RouteItem } from "../stores/itineraryStore";

const props = defineProps<{
  day: DailyRoute | null;
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

function drawRoute() {
  if (!map || !AMapInstance) return;
  clearOverlays();

  const items = validItems(props.day);
  if (!items.length) return;

  const markers = items.map((item, index) => {
    const marker = new AMapInstance.Marker({
      position: [item.longitude, item.latitude],
      title: item.poi_name,
      label: {
        content: `${index + 1}. ${item.poi_name}`,
        direction: "top",
      },
    });

    marker.on("click", () => {
      const info = new AMapInstance.InfoWindow({
        content: `
          <div style="padding:8px 10px;line-height:1.6;min-width:180px">
            <div style="font-weight:700;margin-bottom:4px">${index + 1}. ${item.poi_name}</div>
            <div>类型：${item.poi_type || "-"}</div>
            <div>片区：${item.nearby_area || "-"}</div>
            <div>停留：${item.suggested_duration_minutes || 0} 分钟</div>
            <div>提示：${item.tips || "暂无"}</div>
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

  overlays = [...markers, polyline];
  map.add(overlays);
  map.setFitView(overlays, false, [80, 80, 80, 80]);
}

onMounted(async () => {
  await initMap();
});

watch(
  () => props.day,
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
