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
  destination: string;
  days: number;
  budget: number;
  preferences: string[];
  avoid?: string[];
  travel_style: 'relaxed' | 'standard' | 'intensive';
  walking_tolerance: 'low' | 'medium' | 'high';
  transport_preference: string;
}

export interface RouteItem {
  sort_order: number;
  poi_name: string;
  poi_type: string;
  nearby_area: string;
  suggested_duration_minutes: number;
  reason: string;
}

export interface DailyRoute {
  day_index: number;
  title: string;
  items: RouteItem[];
}

export interface ItineraryPlan {
  plan_type: string;
  title: string;
  summary: string;
  days: DailyRoute[];
}

export interface ItineraryResult {
  itinerary_id: string;
  destination: string;
  plans: ItineraryPlan[];
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
