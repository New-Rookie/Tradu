<template>
  <div>
    <el-alert
      v-if="!configReady"
      title="地图 Key 未配置"
      description="请在 frontend/.env.development 中配置 VITE_AMAP_JS_API_KEY 和 VITE_AMAP_JS_SECURITY_JSCODE。"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 12px"
    />
    <div ref="mapRef" class="map-box"></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import type { PoiItem } from '@/api/types';
import { hasAmapConfig, loadAmap } from '@/utils/amap';

const props = defineProps<{ pois: PoiItem[] }>();
const mapRef = ref<HTMLDivElement | null>(null);
const configReady = hasAmapConfig();
let map: any = null;
let markers: any[] = [];

function clearMarkers() {
  if (map && markers.length > 0) {
    map.remove(markers);
  }
  markers = [];
}

function renderMarkers(AMap: any) {
  if (!map) return;
  clearMarkers();

  markers = props.pois
    .filter((p) => Number.isFinite(p.longitude) && Number.isFinite(p.latitude))
    .map((p) => new AMap.Marker({
      position: [p.longitude, p.latitude],
      title: p.poi_name,
      label: { content: p.poi_name, direction: 'top' },
    }));

  if (markers.length > 0) {
    map.add(markers);
    map.setFitView(markers, false, [80, 80, 80, 80]);
  }
}

async function initMap() {
  if (!mapRef.value || !configReady) return;
  const AMap = await loadAmap();
  map = new AMap.Map(mapRef.value, {
    zoom: 12,
    center: [106.551556, 29.563009],
    viewMode: '2D',
  });
  map.addControl(new AMap.Scale());
  map.addControl(new AMap.ToolBar());
  renderMarkers(AMap);
}

onMounted(() => {
  initMap().catch((err) => console.error(err));
});

watch(() => props.pois, async () => {
  if (!map || !configReady) return;
  const AMap = await loadAmap();
  renderMarkers(AMap);
}, { deep: true });

onBeforeUnmount(() => {
  if (map) {
    map.destroy();
    map = null;
  }
});
</script>
