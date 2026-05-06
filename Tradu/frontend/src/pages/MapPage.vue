<template>
  <main class="page">
    <section class="header-card">
      <div>
        <p class="eyebrow">TravelDu MVP</p>
        <h1>地图路线预览</h1>
        <p class="subtitle">
          当前版本先用点位顺序连线展示每日路线，优先保证 MVP 可演示。后续再接入高德真实道路级路径 polyline。
        </p>
      </div>
      <div class="actions">
        <RouterLink class="secondary" to="/result">返回结果</RouterLink>
        <RouterLink class="primary" to="/planner">重新规划</RouterLink>
      </div>
    </section>

    <section v-if="!store.itinerary" class="empty-card">
      <h2>暂无地图数据</h2>
      <p>请先在规划页生成行程方案。</p>
      <RouterLink class="primary" to="/planner">去规划</RouterLink>
    </section>

    <template v-else>
      <section class="control-card">
        <PlanSelector
          :plans="store.itinerary.plans"
          :model-value="store.selectedPlanIndex"
          @update:model-value="store.selectPlan"
        />
        <DaySelector
          v-if="currentPlan"
          class="day-row"
          :days="currentPlan.days"
          :model-value="store.selectedDayIndex"
          @update:model-value="store.selectDay"
        />
      </section>

      <section class="map-card">
        <AmapRouteMap :day="currentDay" />
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import PlanSelector from "../components/PlanSelector.vue";
import DaySelector from "../components/DaySelector.vue";
import AmapRouteMap from "../components/AmapRouteMap.vue";
import { useItineraryStore } from "../stores/itineraryStore";

const store = useItineraryStore();
const currentPlan = computed(() => store.currentPlan);
const currentDay = computed(() => store.currentDay);
</script>

<style scoped>
.page {
  max-width: 1240px;
  margin: 0 auto;
  padding: 28px 20px 60px;
}

.header-card,
.control-card,
.map-card,
.empty-card {
  background: #fff;
  border: 1px solid #e4e7ec;
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(16, 24, 40, 0.06);
}

.header-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  align-items: center;
}

.eyebrow {
  color: #315efb;
  font-weight: 700;
  margin: 0 0 8px;
}

h1, h2, p {
  margin-top: 0;
}

h1 {
  margin-bottom: 10px;
  font-size: 30px;
  color: #172033;
}

.subtitle {
  max-width: 720px;
  color: #667085;
  line-height: 1.7;
  margin-bottom: 0;
}

.actions {
  display: flex;
  gap: 12px;
}

.primary,
.secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 10px 16px;
  text-decoration: none;
  font-weight: 700;
}

.primary {
  background: #315efb;
  color: #fff;
}

.secondary {
  background: #f2f4f7;
  color: #172033;
}

.control-card,
.empty-card {
  margin-top: 18px;
  padding: 18px;
}

.day-row {
  margin-top: 14px;
}

.map-card {
  margin-top: 18px;
  padding: 12px;
}
</style>
