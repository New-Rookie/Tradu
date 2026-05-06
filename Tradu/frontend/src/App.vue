<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="brand" @click="router.push('/')">
        <span class="brand-mark">旅</span>
        <span>旅渡 TravelDu</span>
      </div>
      <nav class="nav">
        <router-link to="/planner">开始规划</router-link>
        <router-link to="/import-note">导入攻略</router-link>
        <router-link to="/result">方案结果</router-link>
        <router-link to="/map">地图</router-link>
      </nav>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
