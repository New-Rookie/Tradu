<template>
  <section class="page">
    <h1 class="page-title">地图展示</h1>
    <p class="page-subtitle">当前阶段先显示重庆 POI Marker，正式路线 Polyline 后续接入。</p>
    <div class="grid-2">
      <el-card class="card" shadow="never">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px">
            <span>POI 列表</span>
            <el-button size="small" :loading="loading" @click="loadPois">刷新</el-button>
          </div>
        </template>
        <el-alert
          v-if="error"
          :title="error"
          type="error"
          show-icon
          :closable="false"
          style="margin-bottom: 12px"
        />
        <el-scrollbar height="580px">
          <el-timeline>
            <el-timeline-item v-for="poi in store.pois" :key="poi.id" :timestamp="poi.nearby_area">
              <strong>{{ poi.poi_name }}</strong>
              <div class="muted">{{ poi.district }} · {{ poi.poi_type }}</div>
              <div class="tag-row" style="margin-top: 6px">
                <el-tag v-for="tag in poi.tags.slice(0, 3)" :key="tag" size="small">{{ tag }}</el-tag>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-scrollbar>
      </el-card>
      <AmapContainer :pois="store.pois" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { fetchPois } from '@/api/poi';
import { useItineraryStore } from '@/stores/itineraryStore';
import AmapContainer from '@/components/AmapContainer.vue';

const store = useItineraryStore();
const loading = ref(false);
const error = ref('');

async function loadPois() {
  loading.value = true;
  error.value = '';
  try {
    const pois = await fetchPois('重庆');
    store.setPois(pois);
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (store.pois.length === 0) loadPois();
});
</script>
