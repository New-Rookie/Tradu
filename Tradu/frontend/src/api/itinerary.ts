import { apiClient } from './client';
import type { ApiResponse, ItineraryRequest, ItineraryResult } from './types';

export async function generateItinerary(payload: ItineraryRequest) {
  const res = await apiClient.post<ApiResponse<ItineraryResult>>('/api/v1/itineraries/generate', payload);
  return res.data.data;
}
