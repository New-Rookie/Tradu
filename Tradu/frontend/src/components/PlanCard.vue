<template>
  <el-card v-if="plan" class="card" shadow="never">
    <template #header>
      <div>
        <h2>{{ plan.title }}</h2>
        <p class="muted">{{ plan.plan_type }}</p>
      </div>
    </template>
    <p>{{ plan.summary }}</p>
    <el-divider />
    <DayTimeline :days="plan.days" />
  </el-card>
  <el-empty v-else description="暂无行程方案" />
</template>

<script setup lang="ts">
import type { ItineraryPlan } from '@/api/types';
import DayTimeline from './DayTimeline.vue';
defineProps<{ plan: ItineraryPlan | null }>();
</script>

<style scoped>
h2 { margin: 0 0 4px; }
</style>
