<template>
  <el-card class="card" shadow="never">
    <template #header>方案列表</template>
    <div class="plan-list">
      <button
        v-for="(plan, index) in plans"
        :key="`${plan.plan_type}-${index}`"
        class="plan-tab"
        :class="{ active: index === modelValue }"
        @click="$emit('update:modelValue', index)"
      >
        <strong>{{ plan.plan_type }}</strong>
        <span>{{ plan.title }}</span>
      </button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { ItineraryPlan } from '@/api/types';

defineProps<{ plans: ItineraryPlan[]; modelValue: number }>();
defineEmits<{ 'update:modelValue': [value: number] }>();
</script>

<style scoped>
.plan-list { display: flex; flex-direction: column; gap: 10px; }
.plan-tab {
  text-align: left;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  background: #fff;
  cursor: pointer;
}
.plan-tab strong { display: block; margin-bottom: 4px; }
.plan-tab span { color: #6b7280; font-size: 13px; }
.plan-tab.active { border-color: #2563eb; background: #eff6ff; }
</style>
