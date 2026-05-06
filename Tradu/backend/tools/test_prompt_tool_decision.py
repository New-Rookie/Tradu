from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from backend.app.services.deepseek_service import DeepSeekService
from backend.app.schemas.llm_schema import ToolDecisionResult


def main():
    service = DeepSeekService()
    state = {
        "task": "用户导入攻略后生成路线",
        "city": "重庆",
        "extracted_pois": ["洪崖洞", "解放碑", "八一好吃街"],
        "has_weather": False,
        "has_route_matrix": False
    }
    result = service.chat_json("tool_decision.md", json.dumps(state, ensure_ascii=False), ToolDecisionResult)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
