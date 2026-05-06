import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', name: 'home', component: () => import('@/pages/Home.vue') },
  { path: '/planner', name: 'planner', component: () => import('@/pages/Planner.vue') },
  { path: '/import-note', name: 'import-note', component: () => import('@/pages/ImportNote.vue') },
  { path: '/result', name: 'result', component: () => import('@/pages/Result.vue') },
  { path: '/map', name: 'map', component: () => import('@/pages/MapView.vue') },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
