import { defineStore } from 'pinia';
import type { AdjustmentResult, BudgetPlan, DailyRoute, HotelAreaRecommendation, ItineraryPlan, ItineraryRequest, ItineraryResult, NoteExtractResult, PoiItem, RouteItem } from '@/api/types';
import * as itineraryApi from '@/api/itinerary';

export type { DailyRoute, RouteItem } from '@/api/types';

export const useItineraryStore = defineStore('itinerary', {
  state: () => ({
    request: null as ItineraryRequest | null,
    itinerary: null as ItineraryResult | null,
    result: null as ItineraryResult | null,
    currentItinerary: null as ItineraryResult | null,
    budgetPlan: null as BudgetPlan | null,
    recommendedHotelArea: null as HotelAreaRecommendation | null,
    selectedPlanIndex: 0,
    selectedDayIndex: 0,
    removedPois: [] as string[],
    lockedPois: [] as string[],
    adjustmentHistory: [] as Array<Record<string, any>>,
    weatherMode: 'normal',
    pois: [] as PoiItem[],
    extractedNote: null as NoteExtractResult | null,
  }),
  getters: {
    currentPlan(state): ItineraryPlan | null {
      return state.itinerary?.plans?.[state.selectedPlanIndex] ?? null;
    },
    selectedPlan(): ItineraryPlan | null {
      return this.currentPlan;
    },
    currentDay(): DailyRoute | null {
      return this.currentPlan?.days?.[this.selectedDayIndex] ?? null;
    },
  },
  actions: {
    setRequest(payload: ItineraryRequest) {
      this.request = payload;
    },
    setResult(payload: ItineraryResult) {
      this.setItinerary(payload, this.request || undefined);
    },
    setItinerary(payload: ItineraryResult, request?: ItineraryRequest) {
      this.itinerary = payload;
      this.result = payload;
      this.currentItinerary = payload;
      this.request = request ?? this.request;
      this.budgetPlan = payload.budget_plan ?? null;
      this.recommendedHotelArea = payload.recommended_hotel_area ?? null;
      this.selectedPlanIndex = 0;
      this.selectedDayIndex = 0;
    },
    selectPlan(index: number) {
      this.selectedPlanIndex = index;
      this.selectedDayIndex = 0;
    },
    selectDay(index: number) {
      this.selectedDayIndex = index;
    },
    setSelectedPlanIndex(index: number) {
      this.selectPlan(index);
    },
    setPois(pois: PoiItem[]) {
      this.pois = pois;
    },
    setExtractedNote(note: NoteExtractResult) {
      this.extractedNote = note;
    },
    async generateItinerary(payload: ItineraryRequest) {
      const result = await itineraryApi.generateItinerary(payload);
      this.setItinerary(result, payload);
      return result;
    },
    applyAdjustment(result: AdjustmentResult) {
      this.setItinerary(result.itinerary, this.request || undefined);
      this.adjustmentHistory.push({ actions: result.adjustment_actions, explanation: result.explanation, created_at: new Date().toISOString() });
    },
    async adjustItinerary(sessionId: string, instruction: string) {
      const result = await itineraryApi.adjustItinerary({ session_id: sessionId, instruction });
      this.applyAdjustment(result);
      return result;
    },
    async removePoi(sessionId: string, poiName: string) {
      const result = await itineraryApi.removePoi({ session_id: sessionId, poi_name: poiName });
      if (!this.removedPois.includes(poiName)) this.removedPois.push(poiName);
      this.applyAdjustment(result);
      return result;
    },
    async reduceWalking(sessionId: string) {
      const result = await itineraryApi.reduceWalking({ session_id: sessionId });
      this.applyAdjustment(result);
      return result;
    },
    async applyRainMode(sessionId: string) {
      const result = await itineraryApi.applyRainMode({ session_id: sessionId });
      this.weatherMode = 'rainy';
      this.applyAdjustment(result);
      return result;
    },
    async compressDay(sessionId: string, dayIndex: number) {
      const result = await itineraryApi.compressDay({ session_id: sessionId, day_index: dayIndex });
      this.applyAdjustment(result);
      return result;
    },
    async continueFromLocation(sessionId: string, longitude: number, latitude: number) {
      const result = await itineraryApi.continueFromLocation({ session_id: sessionId, longitude, latitude, current_time: new Date().toTimeString().slice(0, 5) });
      this.applyAdjustment(result);
      return result;
    },
  },
});
