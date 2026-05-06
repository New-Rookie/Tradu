<template>
  <main class="page">
    <section class="header-card">
      <div>
        <p class="eyebrow">TravelDu MVP</p>
        <h1>行程方案结果</h1>
        <p class="subtitle">
          当前展示后端正式算法生成的多方案路线。后续可继续接入真实道路级路径与 DeepSeek 深度解释。
        </p>
      </div>
      <div class="actions">
        <RouterLink class="secondary" to="/planner">重新规划</RouterLink>
        <RouterLink class="primary" to="/map">查看地图</RouterLink>
      </div>
    </section>

    <section v-if="!store.itinerary" class="empty-card">
      <h2>暂无行程结果</h2>
      <p>请先在规划页生成一份行程。</p>
      <RouterLink class="primary" to="/planner">去规划</RouterLink>
    </section>

    <template v-else>
      <section class="section-card">
        <div class="section-title-row">
          <div>
            <h2>{{ store.itinerary.destination }}路线方案</h2>
            <p>行程ID：{{ store.itinerary.itinerary_id }}</p>
          </div>
        </div>
        <PlanSelector
          :plans="store.itinerary.plans"
          :model-value="store.selectedPlanIndex"
          @update:model-value="store.selectPlan"
        />
      </section>

      <section v-if="currentPlan" class="section-card">
        <div class="plan-summary">
          <div>
            <h2>{{ currentPlan.title }}</h2>
            <p>{{ currentPlan.summary }}</p>
          </div>
          <div class="metrics">
            <div>
              <strong>{{ currentPlan.score ?? '--' }}</strong>
              <span>评分</span>
            </div>
            <div>
              <strong>{{ currentPlan.total_estimated_cost_low }}-{{ currentPlan.total_estimated_cost_high }}</strong>
              <span>预算</span>
            </div>
            <div>
              <strong>{{ currentPlan.total_walking_distance_km }}</strong>
              <span>步行 km</span>
            </div>
            <div>
              <strong>{{ currentPlan.total_transport_time_minutes }}</strong>
              <span>交通分钟</span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="currentPlan" class="days-grid">
        <article v-for="day in currentPlan.days" :key="day.day_index" class="day-card">
          <div class="day-header">
            <div>
              <h3>{{ day.title }}</h3>
              <p>{{ day.summary }}</p>
            </div>
            <RouterLink class="map-link" to="/map" @click="selectDay(day.day_index)">地图</RouterLink>
          </div>

          <div class="day-metrics">
            <span>片区：{{ day.main_area || '核心片区' }}</span>
            <span>预算：{{ day.estimated_cost_low }}-{{ day.estimated_cost_high }}</span>
            <span>步行：{{ day.walking_distance_km }}km</span>
            <span>交通：{{ day.transport_time_minutes }}分钟</span>
          </div>

          <ol class="timeline">
            <li v-for="item in day.items" :key="itemKey(item)">
              <div class="node">{{ item.sort_order }}</div>
              <div class="item-body">
                <div class="item-title-row">
                  <strong>{{ item.poi_name }}</strong>
                  <span>{{ item.poi_type }}</span>
                </div>
                <p>{{ item.reason }}</p>
                <div class="item-tags">
                  <span v-for="tag in item.tags || []" :key="tag">{{ tag }}</span>
                </div>
                <div class="next-line" v-if="item.transport_to_next">
                  下一站：{{ item.transport_to_next }} · {{ item.distance_to_next_km }}km · {{ item.time_to_next_minutes }}分钟
                </div>
              </div>
            </li>
          </ol>
        </article>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import PlanSelector from "../components/PlanSelector.vue";
import { useItineraryStore, type RouteItem } from "../stores/itineraryStore";

const store = useItineraryStore();
const currentPlan = computed(() => store.currentPlan);

function itemKey(item: RouteItem) {
  return `${item.poi_id ?? item.poi_name}-${item.longitude}-${item.latitude}-${item.sort_order}`;
}

function selectDay(dayIndex: number) {
  store.selectDay(Math.max(0, dayIndex - 1));
}
</script>

<style scoped>
.page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px 20px 60px;
}

.header-card,
.section-card,
.empty-card,
.day-card {
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

h1, h2, h3, p {
  margin-top: 0;
}

h1 {
  margin-bottom: 10px;
  font-size: 30px;
  color: #172033;
}

.subtitle {
  max-width: 680px;
  color: #667085;
  line-height: 1.7;
  margin-bottom: 0;
}

.actions {
  display: flex;
  gap: 12px;
}

.primary,
.secondary,
.map-link {
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

.secondary,
.map-link {
  background: #f2f4f7;
  color: #172033;
}

.section-card,
.empty-card {
  margin-top: 18px;
  padding: 22px;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title-row p {
  color: #667085;
  margin-bottom: 0;
}

.plan-summary {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
}

.plan-summary p {
  color: #667085;
  line-height: 1.7;
  margin-bottom: 0;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, 110px);
  gap: 10px;
}

.metrics div {
  border: 1px solid #e4e7ec;
  border-radius: 16px;
  padding: 12px;
  text-align: center;
}

.metrics strong {
  display: block;
  font-size: 18px;
  color: #172033;
}

.metrics span {
  color: #667085;
  font-size: 12px;
}

.days-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  margin-top: 18px;
}

.day-card {
  padding: 22px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.day-header p {
  color: #667085;
  line-height: 1.7;
  margin-bottom: 0;
}

.day-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 16px 0;
}

.day-metrics span {
  background: #f8fafc;
  border: 1px solid #e4e7ec;
  border-radius: 999px;
  padding: 7px 12px;
  color: #475467;
  font-size: 13px;
}

.timeline {
  list-style: none;
  padding: 0;
  margin: 0;
}

.timeline li {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 14px;
  padding: 14px 0;
  border-top: 1px solid #eef2f6;
}

.node {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #315efb;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.item-title-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-title-row span {
  color: #667085;
  font-size: 13px;
}

.item-body p {
  color: #667085;
  line-height: 1.6;
  margin: 6px 0;
}

.item-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.item-tags span {
  padding: 4px 8px;
  border-radius: 999px;
  background: #eef3ff;
  color: #315efb;
  font-size: 12px;
}

.next-line {
  margin-top: 8px;
  color: #475467;
  font-size: 13px;
}
</style>
