<template>
  <section class="page">
    <h1 class="page-title">需求填写</h1>
    <p class="page-subtitle">先完成“用户需求 → 后端行程生成 → 前端展示”的闭环。</p>
    <div class="grid-2">
      <el-card class="card" shadow="never">
        <template #header>旅行需求</template>
        <PreferenceForm :loading="loading" @submit="handleSubmit" />
      </el-card>
      <el-card class="card" shadow="never">
        <template #header>联调状态</template>
        <el-alert
          title="当前仍是 API 骨架阶段"
          description="生成结果来自后端 simple_itinerary_service，后续第八步会接入正式评分、路线距离和预算估算。"
          type="info"
          show-icon
          :closable="false"
        />
        <pre v-if="lastPayload">{{ JSON.stringify(lastPayload, null, 2) }}</pre>
      </el-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import PreferenceForm from '@/components/PreferenceForm.vue';
import { generateItinerary } from '@/api/itinerary';
import type { ItineraryRequest } from '@/api/types';
import { useItineraryStore } from '@/stores/itineraryStore';

const router = useRouter();
const store = useItineraryStore();
const loading = ref(false);
const lastPayload = ref<ItineraryRequest | null>(null);

async function handleSubmit(payload: ItineraryRequest) {
  loading.value = true;
  lastPayload.value = payload;
  try {
    const result = await generateItinerary(payload);
    store.setRequest(payload);
    store.setResult(result);
    ElMessage.success('行程方案已生成');
    router.push('/result');
  } catch (err) {
    ElMessage.error((err as Error).message);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
pre { white-space: pre-wrap; background: #f9fafb; border-radius: 12px; padding: 14px; margin-top: 16px; }
</style>
