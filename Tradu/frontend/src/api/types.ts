export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PoiItem {
  id: number;
  poi_name: string;
  city: string;
  district: string;
  poi_type: string;
  tags: string[];
  nearby_area: string;
  longitude: number;
  latitude: number;
  amap_poi_id?: string;
  recommended_duration_minutes?: number;
  best_time?: string;
  price_level?: string;
  indoor_outdoor?: string;
  avoid_tips?: string;
  match_status?: string;
}

export interface ItineraryRequest {
  session_id?: string;
  destination: string;
  days: number;
  budget: number;
  preferences: string[];
  avoid?: string[];
  travel_style: 'relaxed' | 'standard' | 'intensive';
  walking_tolerance: 'low' | 'medium' | 'high';
  transport_preference: string;
  need_meal_planning?: boolean;
  need_hotel_area?: boolean;
  budget_control_level?: string;
}

export interface BudgetPlan {
  total_budget: number;
  days: number;
  accommodation_budget: number;
  food_budget: number;
  attraction_budget: number;
  transport_budget: number;
  buffer_budget: number;
  daily_food_budget: number;
  daily_transport_budget: number;
  budget_warning: string;
  budget_control_hint: string;
}

export interface HotelAreaRecommendation {
  item_type?: 'hotel_area';
  area_name: string;
  poi_name?: string;
  budget_level: string;
  longitude?: number;
  latitude?: number;
  reason: string;
  risk_tips: string[];
  reference_hotels?: Array<Record<string, any>>;
}

export interface RouteItem {
  sort_order: number;
  item_type?: 'attraction' | 'meal' | 'hotel_area' | 'rest';
  meal_type?: 'lunch' | 'dinner';
  poi_id?: number | null;
  poi_name: string;
  poi_type: string;
  service_type?: string;
  nearby_area: string;
  longitude?: number;
  latitude?: number;
  tags?: string[];
  suggested_duration_minutes: number;
  estimated_cost_low?: number;
  estimated_cost_high?: number;
  distance_to_next_km?: number;
  walking_to_next_km?: number;
  time_to_next_minutes?: number;
  transport_to_next?: string;
  reason: string;
  tips?: string;
}

export interface DailyRoute {
  day_index: number;
  title: string;
  summary: string;
  main_area?: string;
  estimated_cost_low?: number;
  estimated_cost_high?: number;
  walking_distance_km?: number;
  transport_distance_km?: number;
  transport_time_minutes?: number;
  budget_detail?: Record<string, any>;
  items: RouteItem[];
}

export interface ItineraryPlan {
  plan_type: string;
  title: string;
  summary: string;
  score?: number;
  total_estimated_cost_low?: number;
  total_estimated_cost_high?: number;
  total_walking_distance_km?: number;
  total_transport_distance_km?: number;
  total_transport_time_minutes?: number;
  budget_summary?: Record<string, any>;
  budget_warnings?: string[];
  recommended_hotel_area?: HotelAreaRecommendation | null;
  days: DailyRoute[];
}

export interface ItineraryResult {
  itinerary_id: string;
  destination: string;
  budget_plan?: BudgetPlan;
  budget_summary?: Record<string, any>;
  budget_warnings?: string | string[];
  recommended_hotel_area?: HotelAreaRecommendation | null;
  plans: ItineraryPlan[];
}

export interface AdjustmentResult {
  adjustment_actions: Array<Record<string, any>>;
  itinerary: ItineraryResult;
  explanation: string;
}

export interface ExtractedPoi {
  raw_name: string;
  normalized_name: string;
  poi_type: string;
  tags: string[];
  recommended_time: string;
  suggested_duration_minutes: number;
  tips: string[];
  confidence: number;
}

export interface NoteExtractResult {
  city: string;
  pois: ExtractedPoi[];
  global_tips: string[];
  detected_days?: number;
}
