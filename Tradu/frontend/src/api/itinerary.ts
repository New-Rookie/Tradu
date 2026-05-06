import { apiClient } from './client';
import type { AdjustmentResult, ApiResponse, ItineraryRequest, ItineraryResult } from './types';

export async function generateItinerary(payload: ItineraryRequest) {
  const res = await apiClient.post<ApiResponse<ItineraryResult>>('/api/v1/itineraries/generate', payload);
  return res.data.data;
}

export async function adjustItinerary(payload: { session_id: string; instruction: string }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/adjust', payload);
  return res.data.data.data;
}

export async function reduceWalking(payload: { session_id: string }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/reduce-walking', payload);
  return res.data.data.data;
}

export async function applyRainMode(payload: { session_id: string }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/rain-mode', payload);
  return res.data.data.data;
}

export async function removePoi(payload: { session_id: string; poi_name: string }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/remove-poi', payload);
  return res.data.data.data;
}

export async function compressDay(payload: { session_id: string; day_index: number }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/compress-day', payload);
  return res.data.data.data;
}

export async function continueFromLocation(payload: { session_id: string; longitude: number; latitude: number; current_time?: string }) {
  const res = await apiClient.post<ApiResponse<{ success: boolean; data: AdjustmentResult }>>('/api/v1/itineraries/continue-from-location', payload);
  return res.data.data.data;
}
