import { apiClient } from './client';
import type { ApiResponse, PoiItem } from './types';

export async function fetchPois(city = '重庆') {
  const res = await apiClient.get<ApiResponse<PoiItem[]>>('/api/v1/pois', {
    params: { city },
  });
  return res.data.data;
}
