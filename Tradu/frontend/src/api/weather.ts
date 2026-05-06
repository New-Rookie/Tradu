import { apiClient } from './client';
import type { ApiResponse } from './types';

export async function fetchWeather(city = '重庆') {
  const res = await apiClient.get<ApiResponse<Record<string, unknown>>>('/api/v1/weather', {
    params: { city },
  });
  return res.data.data;
}
