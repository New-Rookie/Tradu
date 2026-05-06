from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from backend.app.services.deepseek_service import DeepSeekService
from backend.app.schemas.llm_schema import ItineraryExplanation


def main():
    service = DeepSeekService()
    itinerary = {
        "plan_type": "少走路轻松方案",
        "destination": "重庆",
        "days": [
            {
                "day_index": 1,
                "items": [
                    {"poi_name": "解放碑", "start_time": "09:30", "end_time": "11:00", "nearby_area": "解放碑片区"},
                    {"poi_name": "八一好吃街", "start_time": "11:30", "end_time": "12:30", "nearby_area": "解放碑片区"},
                    {"poi_name": "洪崖洞", "start_time": "19:00", "end_time": "20:30", "nearby_area": "解放碑片区"}
                ]
            }
        ]
    }
    result = service.chat_json("itinerary_explainer.md", json.dumps(itinerary, ensure_ascii=False), ItineraryExplanation)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
