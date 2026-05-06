<template>
  <section class="page">
    <h1 class="page-title">导入攻略</h1>
    <p class="page-subtitle">粘贴攻略文本，调用后端 DeepSeek 抽取地点。</p>
    <div class="grid-2">
      <el-card class="card" shadow="never">
        <template #header>攻略文本</template>
        <el-input
          v-model="noteText"
          type="textarea"
          :rows="14"
          placeholder="粘贴小红书或其他攻略文本。V1 不做自动爬取，只处理用户主动导入文本。"
        />
        <div class="action-row">
          <el-button type="primary" :loading="loading" @click="handleExtract">提取地点</el-button>
          <el-button @click="fillDemo">填入示例</el-button>
        </div>
      </el-card>

      <el-card class="card" shadow="never">
        <template #header>识别结果</template>
        <el-empty v-if="!store.extractedNote" description="暂无识别结果" />
        <div v-else>
          <p><strong>城市：</strong>{{ store.extractedNote.city }}</p>
          <div class="tag-row" style="margin-bottom: 16px">
            <el-tag v-for="poi in store.extractedNote.pois" :key="poi.raw_name" type="success">
              {{ poi.normalized_name }} · {{ poi.poi_type }}
            </el-tag>
          </div>
          <el-alert
            v-if="store.extractedNote.global_tips.length"
            :title="store.extractedNote.global_tips.join('；')"
            type="warning"
            show-icon
            :closable="false"
          />
        </div>
      </el-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { extractNote } from '@/api/content';
import { useItineraryStore } from '@/stores/itineraryStore';

const store = useItineraryStore();
const loading = ref(false);
const noteText = ref('');

function fillDemo() {
  noteText.value = '重庆三日游推荐：第一天解放碑、八一好吃街、洪崖洞和千厮门大桥。第二天山城步道、十八梯、白象居。第三天鹅岭二厂、李子坝、观音桥。洪崖洞节假日人很多，建议晚上从桥上拍远景。';
}

async function handleExtract() {
  if (!noteText.value.trim()) {
    ElMessage.warning('请先粘贴攻略文本');
    return;
  }
  loading.value = true;
  try {
    const result = await extractNote(noteText.value);
    store.setExtractedNote(result);
    ElMessage.success('地点提取完成');
  } catch (err) {
    ElMessage.error((err as Error).message);
  } finally {
    loading.value = false;
  }
}
</script>
