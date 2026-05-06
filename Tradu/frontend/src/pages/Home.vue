<template>
  <section class="page home-page">
    <el-card class="hero-card" shadow="never">
      <div class="hero-content">
        <div>
          <p class="eyebrow">TravelDu V1</p>
          <h1>把旅行攻略转成可执行路线</h1>
          <p class="hero-text">
            旅渡基于 DeepSeek、高德地图和本地 POI 知识库，将目的地、天数、预算和偏好转化为本地旅行方案。
          </p>
          <div class="action-row">
            <el-button type="primary" size="large" @click="router.push('/planner')">开始规划</el-button>
            <el-button size="large" @click="router.push('/import-note')">导入攻略</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="panel-item"><strong>01</strong><span>理解用户意图</span></div>
          <div class="panel-item"><strong>02</strong><span>匹配重庆 POI</span></div>
          <div class="panel-item"><strong>03</strong><span>生成多套方案</span></div>
          <div class="panel-item"><strong>04</strong><span>地图展示点位</span></div>
        </div>
      </div>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
</script>

<style scoped>
.hero-card { border-radius: 24px; min-height: 520px; display: flex; align-items: center; }
.hero-content { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 48px; width: 100%; align-items: center; padding: 34px; }
.eyebrow { color: #2563eb; font-weight: 700; }
h1 { font-size: 48px; line-height: 1.1; margin: 0 0 18px; }
.hero-text { color: #6b7280; font-size: 18px; line-height: 1.8; }
.hero-panel { display: grid; gap: 14px; }
.panel-item { display: flex; align-items: center; gap: 14px; padding: 18px; border-radius: 16px; background: #f3f4f6; }
.panel-item strong { color: #2563eb; }
@media (max-width: 900px) { .hero-content { grid-template-columns: 1fr; } h1 { font-size: 36px; } }
</style>
