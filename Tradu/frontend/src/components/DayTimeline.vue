<template>
  <div class="day-timeline">
    <el-card v-for="day in days" :key="day.day_index" class="card day-card" shadow="never">
      <template #header>
        <strong>{{ day.title || `Day ${day.day_index}` }}</strong>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="item in day.items"
          :key="`${day.day_index}-${item.sort_order}-${item.poi_name}`"
          :timestamp="`${item.suggested_duration_minutes} 分钟`"
          placement="top"
        >
          <div class="poi-title">{{ item.sort_order }}. {{ item.poi_name }}</div>
          <div class="muted">{{ item.poi_type }} · {{ item.nearby_area }}</div>
          <p>{{ item.reason }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { DailyRoute } from '@/api/types';
defineProps<{ days: DailyRoute[] }>();
</script>

<style scoped>
.day-timeline { display: flex; flex-direction: column; gap: 16px; }
.day-card { margin-bottom: 0; }
.poi-title { font-weight: 700; margin-bottom: 4px; }
p { margin: 6px 0 0; }
</style>
