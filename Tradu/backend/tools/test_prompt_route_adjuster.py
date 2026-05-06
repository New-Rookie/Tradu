from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from backend.app.services.deepseek_service import DeepSeekService
from backend.app.schemas.llm_schema import RouteAdjustIntent


def main():
    service = DeepSeekService()
    text = "我不想去洪崖洞，人太多了，能不能少走路，多安排点美食？"
    result = service.chat_json("route_adjuster.md", text, RouteAdjustIntent)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
