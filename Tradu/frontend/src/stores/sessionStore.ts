import { defineStore } from 'pinia';
import { apiClient } from '@/api/client';
import type { ApiResponse } from '@/api/types';

const STORAGE_KEY = 'tradu_session_id';

export const useSessionStore = defineStore('session', {
  state: () => ({
    sessionId: localStorage.getItem(STORAGE_KEY) || '',
    initialized: false,
    currentDestination: '',
    currentItineraryId: '',
  }),
  actions: {
    async initSession() {
      if (this.initialized && this.sessionId) return this.sessionId;
      const existing = localStorage.getItem(STORAGE_KEY) || this.sessionId || undefined;
      const res = await apiClient.post<ApiResponse<{ session_id: string; status: string }>>('/api/v1/sessions', { session_id: existing });
      this.sessionId = res.data.data.session_id;
      this.initialized = true;
      localStorage.setItem(STORAGE_KEY, this.sessionId);
      return this.sessionId;
    },
    getSessionId() {
      return this.sessionId || localStorage.getItem(STORAGE_KEY) || '';
    },
    clearSession() {
      this.sessionId = '';
      this.initialized = false;
      this.currentDestination = '';
      this.currentItineraryId = '';
      localStorage.removeItem(STORAGE_KEY);
    },
  },
});
