from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from backend.app.services.deepseek_service import DeepSeekService
from backend.app.schemas.llm_schema import TravelIntent


def main():
    service = DeepSeekService()
    text = "我想去重庆玩3天，预算2500，喜欢美食、拍照和夜景，不想太累，尽量坐地铁。"
    result = service.chat_json("intent_parser.md", text, TravelIntent)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
