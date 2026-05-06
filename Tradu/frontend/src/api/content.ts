import { apiClient } from './client';
import type { ApiResponse, NoteExtractResult } from './types';

export async function extractNote(text: string) {
  const res = await apiClient.post<ApiResponse<NoteExtractResult>>('/api/v1/content/extract', { text });
  return res.data.data;
}
