<template>
  <div class="plan-selector">
    <button
      v-for="(plan, index) in plans"
      :key="plan.plan_type + index"
      class="plan-button"
      :class="{ active: index === modelValue }"
      @click="$emit('update:modelValue', index)"
    >
      <div class="plan-title">{{ plan.plan_type }}</div>
      <div class="plan-meta">
        分数 {{ formatNumber(plan.score) }} · {{ plan.days?.length || 0 }} 天
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { ItineraryPlan } from "../stores/itineraryStore";

const props = defineProps<{
  plans: ItineraryPlan[];
  modelValue: number;
}>();

def formatNumber(value?: number) {
  if (value === undefined || value === null) return "--";
  return Number(value).toFixed(1);
}
</script>

<style scoped>
.plan-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.plan-button {
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  padding: 12px 14px;
  background: #ffffff;
  text-align: left;
  cursor: pointer;
  transition: all 0.18s ease;
}

.plan-button:hover {
  border-color: #6b8afd;
  box-shadow: 0 6px 18px rgba(34, 52, 99, 0.08);
}

.plan-button.active {
  border-color: #315efb;
  background: #eef3ff;
}

.plan-title {
  font-size: 15px;
  font-weight: 700;
  color: #172033;
}

.plan-meta {
  margin-top: 6px;
  color: #667085;
  font-size: 12px;
}
</style>
