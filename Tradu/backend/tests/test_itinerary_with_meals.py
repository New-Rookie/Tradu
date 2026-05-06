from backend.app.services.formal_itinerary_service import FormalItineraryService


def test_itinerary_contains_lunch_and_dinner():
    result = FormalItineraryService().generate_itinerary({
        "destination": "重庆",
        "days": 2,
        "budget": 2500,
        "preferences": ["美食", "夜景"],
        "travel_style": "relaxed",
        "need_meal_planning": True,
        "need_hotel_area": True,
    })
    assert len(result["plans"]) == 5
    for day in result["plans"][0]["days"]:
        meals = [i.get("meal_type") for i in day["items"] if i.get("item_type") == "meal"]
        assert "lunch" in meals
        assert "dinner" in meals
        assert day["estimated_cost_high"] > 0
