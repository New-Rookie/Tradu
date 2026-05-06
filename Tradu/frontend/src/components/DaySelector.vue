<template>
  <div class="day-selector">
    <button
      v-for="(day, index) in days"
      :key="day.day_index"
      class="day-button"
      :class="{ active: index === modelValue }"
      @click="$emit('update:modelValue', index)"
    >
      Day {{ day.day_index }}
      <span v-if="day.main_area">{{ day.main_area }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { DailyRoute } from "../stores/itineraryStore";

defineProps<{
  days: DailyRoute[];
  modelValue: number;
}>();
</script>

<style scoped>
.day-selector {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.day-button {
  border: 1px solid #d9e2ec;
  background: #fff;
  border-radius: 999px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 14px;
}

.day-button span {
  margin-left: 6px;
  color: #667085;
}

.day-button.active {
  background: #172033;
  color: #fff;
  border-color: #172033;
}

.day-button.active span {
  color: #d8def0;
}
</style>
