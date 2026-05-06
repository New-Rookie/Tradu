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

      <section class="section-card v1-grid">
        <div v-if="store.recommendedHotelArea" class="v1-card">
          <h3>推荐住宿区域：{{ store.recommendedHotelArea.area_name }}</h3>
          <p>{{ store.recommendedHotelArea.reason }}</p>
          <div class="item-tags">
            <span v-for="tip in store.recommendedHotelArea.risk_tips" :key="tip">{{ tip }}</span>
          </div>
        </div>
        <div v-if="store.budgetPlan" class="v1-card budget-list">
          <h3>预算约束估算</h3>
          <span>总预算：{{ store.budgetPlan.total_budget }}</span>
          <span>住宿：{{ store.budgetPlan.accommodation_budget }}</span>
          <span>餐饮：{{ store.budgetPlan.food_budget }}</span>
          <span>景点：{{ store.budgetPlan.attraction_budget }}</span>
          <span>市内交通：{{ store.budgetPlan.transport_budget }}</span>
          <span>机动：{{ store.budgetPlan.buffer_budget }}</span>
          <strong>风险：{{ store.budgetPlan.budget_warning }}</strong>
        </div>
      </section>

      <section v-if="currentPlan" class="section-card">
        <div class="adjust-bar">
          <button @click="reduceWalking">一键少走路</button>
          <button @click="rainMode">雨天方案</button>
          <button @click="compressToday">压缩当前天</button>
          <button @click="continueFromLocation">从当前位置继续</button>
        </div>
        <div class="adjust-input">
          <input v-model="instruction" placeholder="例如：我不想去洪崖洞，少走路一点，多安排美食" />
          <button @click="submitAdjustment">调整路线</button>
        </div>
        <p v-if="lastExplanation" class="explain">{{ lastExplanation }}</p>
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
                  <span>{{ item.item_type === "meal" ? (item.meal_type === "lunch" ? "午餐" : "晚餐") : item.poi_type }}</span>
                  <button v-if="item.item_type !== 'meal'" class="remove-btn" @click="removePoi(item.poi_name)">删除</button>
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
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import PlanSelector from "../components/PlanSelector.vue";
import { useItineraryStore, type RouteItem } from "../stores/itineraryStore";
import { useSessionStore } from "../stores/sessionStore";

const store = useItineraryStore();
const sessionStore = useSessionStore();
const instruction = ref("");
const lastExplanation = ref("");
const currentPlan = computed(() => store.currentPlan);

function itemKey(item: RouteItem) {
  return `${item.poi_id ?? item.poi_name}-${item.longitude}-${item.latitude}-${item.sort_order}`;
}

function selectDay(dayIndex: number) {
  store.selectDay(Math.max(0, dayIndex - 1));
}

async function withSession() {
  return sessionStore.getSessionId() || await sessionStore.initSession();
}

async function submitAdjustment() {
  if (!instruction.value.trim()) return;
  const result = await store.adjustItinerary(await withSession(), instruction.value.trim());
  lastExplanation.value = result.explanation;
  instruction.value = "";
}

async function removePoi(name: string) {
  const result = await store.removePoi(await withSession(), name);
  lastExplanation.value = result.explanation;
}

async function reduceWalking() {
  const result = await store.reduceWalking(await withSession());
  lastExplanation.value = result.explanation;
}

async function rainMode() {
  const result = await store.applyRainMode(await withSession());
  lastExplanation.value = result.explanation;
}

async function compressToday() {
  const result = await store.compressDay(await withSession(), store.selectedDayIndex + 1);
  lastExplanation.value = result.explanation;
}

async function continueFromLocation() {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const result = await store.continueFromLocation(await withSession(), pos.coords.longitude, pos.coords.latitude);
    lastExplanation.value = result.explanation;
  });
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

<style scoped>
.v1-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.v1-card { border: 1px solid #e4e7ec; border-radius: 16px; padding: 16px; }
.budget-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.budget-list h3 { grid-column: 1 / -1; }
.adjust-bar, .adjust-input { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
.adjust-bar button, .adjust-input button, .remove-btn { border: 0; border-radius: 999px; padding: 8px 12px; background: #eef4ff; color: #315efb; font-weight: 700; cursor: pointer; }
.adjust-input input { flex: 1; min-width: 280px; border: 1px solid #d0d5dd; border-radius: 999px; padding: 10px 14px; }
.explain { color: #315efb; font-weight: 700; }
.remove-btn { margin-left: 8px; background: #fff1f3; color: #c01048; }
</style>
