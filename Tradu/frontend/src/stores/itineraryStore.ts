import { defineStore } from 'pinia';
import type { ItineraryPlan, ItineraryRequest, ItineraryResult, NoteExtractResult, PoiItem } from '@/api/types';

export const useItineraryStore = defineStore('itinerary', {
  state: () => ({
    request: null as ItineraryRequest | null,
    result: null as ItineraryResult | null,
    selectedPlanIndex: 0,
    pois: [] as PoiItem[],
    extractedNote: null as NoteExtractResult | null,
  }),
  getters: {
    selectedPlan(state): ItineraryPlan | null {
      return state.result?.plans?.[state.selectedPlanIndex] ?? null;
    },
  },
  actions: {
    setRequest(payload: ItineraryRequest) {
      this.request = payload;
    },
    setResult(payload: ItineraryResult) {
      this.result = payload;
      this.selectedPlanIndex = 0;
    },
    setSelectedPlanIndex(index: number) {
      this.selectedPlanIndex = index;
    },
    setPois(pois: PoiItem[]) {
      this.pois = pois;
    },
    setExtractedNote(note: NoteExtractResult) {
      this.extractedNote = note;
    },
  },
});
