<template>
  <section class="page">
    <h1 class="page-title">方案结果</h1>
    <p class="page-subtitle">展示后端返回的临时行程方案。正式规划算法将在下一阶段接入。</p>

    <el-empty v-if="!store.result" description="暂无行程，请先生成方案">
      <el-button type="primary" @click="router.push('/planner')">去生成</el-button>
    </el-empty>

    <div v-else class="plan-layout">
      <div>
        <PlanSwitcher
          :plans="store.result.plans"
          :model-value="store.selectedPlanIndex"
          @update:model-value="store.setSelectedPlanIndex"
        />
        <BudgetPanel style="margin-top: 16px" />
        <div class="action-row">
          <el-button type="primary" @click="router.push('/map')">查看地图</el-button>
          <el-button @click="router.push('/planner')">重新规划</el-button>
        </div>
      </div>
      <PlanCard :plan="store.selectedPlan" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useItineraryStore } from '@/stores/itineraryStore';
import PlanSwitcher from '@/components/PlanSwitcher.vue';
import PlanCard from '@/components/PlanCard.vue';
import BudgetPanel from '@/components/BudgetPanel.vue';

const router = useRouter();
const store = useItineraryStore();
</script>
