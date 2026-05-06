import json
from pathlib import Path
from typing import Any, Dict

from openai import OpenAI

from backend.app.core.config import get_settings


PROMPT_DIR = Path("backend/app/prompts")


class DeepSeekApiService:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.deepseek_api_key:
            raise RuntimeError("Missing DEEPSEEK_API_KEY in .env")
        self.client = OpenAI(
            api_key=self.settings.deepseek_api_key,
            base_url=self.settings.deepseek_base_url,
        )

    def _load_prompt(self, filename: str, fallback: str) -> str:
        path = PROMPT_DIR / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return fallback

    def call_json_prompt(self, prompt_file: str, user_input: str, fallback_prompt: str) -> Dict[str, Any]:
        system_prompt = self._load_prompt(prompt_file, fallback_prompt)
        response = self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def parse_intent(self, text: str) -> Dict[str, Any]:
        fallback = """
你是旅渡 TravelDu 的用户需求解析器。请只输出 json。
字段包括 destination, days, budget, preferences, avoid, travel_style, walking_tolerance, transport_preference, missing_fields, clarifying_question。
"""
        return self.call_json_prompt("intent_parser.md", text, fallback)

    def extract_note(self, text: str) -> Dict[str, Any]:
        fallback = """
你是旅渡 TravelDu 的攻略文本地点抽取器。请只输出 json。
字段包括 city, pois, global_tips, detected_days。pois 内部包括 raw_name, normalized_name, poi_type, tags, recommended_time, suggested_duration_minutes, tips, confidence。
"""
        return self.call_json_prompt("note_extractor.md", text, fallback)

    def parse_adjustment(self, text: str) -> Dict[str, Any]:
        fallback = """
你是旅渡 TravelDu 的路线调整指令解析器。请只输出 json。
字段包括 actions, priority, need_regenerate, user_message。
"""
        return self.call_json_prompt("route_adjuster.md", text, fallback)
