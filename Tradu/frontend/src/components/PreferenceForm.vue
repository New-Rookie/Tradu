<template>
  <el-form label-position="top" class="planner-form">
    <el-form-item label="目的地城市">
      <el-input v-model="form.destination" placeholder="例如：重庆" />
    </el-form-item>

    <el-row :gutter="12">
      <el-col :span="12">
        <el-form-item label="出行天数">
          <el-input-number v-model="form.days" :min="1" :max="7" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="预算上限">
          <el-input-number v-model="form.budget" :min="0" :step="100" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="偏好标签">
      <el-select v-model="form.preferences" multiple filterable style="width: 100%">
        <el-option v-for="tag in preferenceOptions" :key="tag" :label="tag" :value="tag" />
      </el-select>
    </el-form-item>

    <el-form-item label="不喜欢 / 避免">
      <el-select v-model="form.avoid" multiple filterable allow-create style="width: 100%">
        <el-option v-for="tag in avoidOptions" :key="tag" :label="tag" :value="tag" />
      </el-select>
    </el-form-item>

    <el-form-item label="旅行强度">
      <el-radio-group v-model="form.travel_style">
        <el-radio-button label="relaxed">轻松</el-radio-button>
        <el-radio-button label="standard">标准</el-radio-button>
        <el-radio-button label="intensive">高强度</el-radio-button>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="步行接受度">
      <el-radio-group v-model="form.walking_tolerance">
        <el-radio-button label="low">低</el-radio-button>
        <el-radio-button label="medium">中</el-radio-button>
        <el-radio-button label="high">高</el-radio-button>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="交通偏好">
      <el-select v-model="form.transport_preference" style="width: 100%">
        <el-option label="公共交通+步行" value="public_transport" />
        <el-option label="打车优先" value="taxi" />
        <el-option label="步行优先" value="walking" />
      </el-select>
    </el-form-item>

    <el-button type="primary" :loading="loading" @click="submit">生成行程</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import type { ItineraryRequest } from '@/api/types';

const props = defineProps<{ loading?: boolean }>();
const emit = defineEmits<{ submit: [payload: ItineraryRequest] }>();

const preferenceOptions = ['美食', '拍照', '夜景', 'citywalk', '历史人文', '亲子', '低预算', '商圈', '博物馆'];
const avoidOptions = ['高强度路线', '长时间排队', '跨区移动', '雨天户外', '人流密集'];

const form = reactive<ItineraryRequest>({
  destination: '重庆',
  days: 3,
  budget: 2500,
  preferences: ['美食', '拍照', '夜景'],
  avoid: ['高强度路线'],
  travel_style: 'relaxed',
  walking_tolerance: 'medium',
  transport_preference: 'public_transport',
});

function submit() {
  emit('submit', { ...form, preferences: [...form.preferences], avoid: [...(form.avoid ?? [])] });
}
</script>
