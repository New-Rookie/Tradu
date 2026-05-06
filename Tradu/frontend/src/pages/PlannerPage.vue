<template>
  <main class="page">
    <section class="hero-card">
      <p class="eyebrow">TravelDu MVP</p>
      <h1>生成你的重庆本地旅行路线</h1>
      <p>输入目的地、天数、预算和偏好，系统会调用后端正式规划接口生成 5 套路线。</p>
    </section>

    <section class="form-card">
      <div class="form-grid">
        <label>
          <span>目的地</span>
          <input v-model="form.destination" placeholder="重庆" />
        </label>
        <label>
          <span>天数</span>
          <input v-model.number="form.days" type="number" min="1" max="7" />
        </label>
        <label>
          <span>预算</span>
          <input v-model.number="form.budget" type="number" min="0" />
        </label>
        <label>
          <span>旅行风格</span>
          <select v-model="form.travel_style">
            <option value="relaxed">轻松游</option>
            <option value="standard">标准游</option>
            <option value="intensive">高强度打卡</option>
          </select>
        </label>
        <label>
          <span>步行接受度</span>
          <select v-model="form.walking_tolerance">
            <option value="low">不想多走</option>
            <option value="medium">正常步行</option>
            <option value="high">可以多走</option>
          </select>
        </label>
        <label>
          <span>交通偏好</span>
          <select v-model="form.transport_preference">
            <option value="public_transport">公共交通/打车</option>
            <option value="walking">尽量步行</option>
            <option value="taxi">优先打车</option>
          </select>
        </label>
      </div>

      <div class="tag-section">
        <div class="section-label">偏好标签</div>
        <div class="tags">
          <button
            v-for="tag in preferenceOptions"
            :key="tag"
            :class="{ active: form.preferences.includes(tag) }"
            @click="togglePreference(tag)"
            type="button"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <div class="tag-section">
        <div class="section-label">不喜欢 / 规避</div>
        <div class="tags">
          <button
            v-for="tag in avoidOptions"
            :key="tag"
            :class="{ active: form.avoid.includes(tag) }"
            @click="toggleAvoid(tag)"
            type="button"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <div class="actions">
        <button class="primary" :disabled="loading" @click="submit">
          {{ loading ? "生成中..." : "生成路线" }}
        </button>
        <RouterLink class="secondary" to="/import-note">导入攻略</RouterLink>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { generateItinerary } from "../api/itinerary";
import { useItineraryStore } from "../stores/itineraryStore";

const router = useRouter();
const store = useItineraryStore();
const loading = ref(false);
const error = ref("");

const preferenceOptions = ["美食", "拍照", "夜景", "citywalk", "历史人文", "商圈", "亲子", "低预算"];
const avoidOptions = ["高强度路线", "长时间排队", "跨区太多", "户外太多", "人流密集"];

const form = reactive({
  destination: "重庆",
  days: 3,
  budget: 2500,
  preferences: ["美食", "拍照", "夜景"],
  avoid: ["高强度路线"],
  travel_style: "relaxed",
  walking_tolerance: "medium",
  transport_preference: "public_transport",
});

function togglePreference(tag: string) {
  const idx = form.preferences.indexOf(tag);
  if (idx >= 0) form.preferences.splice(idx, 1);
  else form.preferences.push(tag);
}

function toggleAvoid(tag: string) {
  const idx = form.avoid.indexOf(tag);
  if (idx >= 0) form.avoid.splice(idx, 1);
  else form.avoid.push(tag);
}

async function submit() {
  loading.value = true;
  error.value = "";
  try {
    const payload = { ...form };
    const res = await generateItinerary(payload);
    if (!res?.success) {
      throw new Error(res?.message || "生成失败");
    }
    store.setItinerary(res.data, payload);
    router.push("/result");
  } catch (err: any) {
    error.value = err?.message || "生成失败，请检查后端是否启动。";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 28px 20px 60px;
}

.hero-card,
.form-card {
  background: #fff;
  border: 1px solid #e4e7ec;
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(16, 24, 40, 0.06);
}

.hero-card {
  padding: 32px;
}

.eyebrow {
  color: #315efb;
  font-weight: 700;
  margin: 0 0 8px;
}

h1, p {
  margin-top: 0;
}

h1 {
  font-size: 32px;
  color: #172033;
  margin-bottom: 10px;
}

.hero-card p:last-child {
  color: #667085;
  line-height: 1.7;
  margin-bottom: 0;
}

.form-card {
  margin-top: 18px;
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

label span,
.section-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: #172033;
}

input,
select {
  width: 100%;
  border: 1px solid #d0d5dd;
  border-radius: 12px;
  padding: 11px 12px;
  font-size: 14px;
  box-sizing: border-box;
}

.tag-section {
  margin-top: 22px;
}

.tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tags button {
  border: 1px solid #d0d5dd;
  background: #fff;
  border-radius: 999px;
  padding: 8px 14px;
  cursor: pointer;
}

.tags button.active {
  background: #315efb;
  border-color: #315efb;
  color: #fff;
}

.actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
}

.primary,
.secondary {
  border: 0;
  border-radius: 999px;
  padding: 11px 18px;
  font-weight: 800;
  cursor: pointer;
  text-decoration: none;
}

.primary {
  background: #315efb;
  color: #fff;
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary {
  background: #f2f4f7;
  color: #172033;
}

.error {
  margin-top: 16px;
  color: #d92d20;
}
</style>
