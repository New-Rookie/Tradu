from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from backend.app.services.deepseek_service import DeepSeekService
from backend.app.schemas.llm_schema import NoteExtractionResult


def main():
    service = DeepSeekService()
    text = """
重庆三日游推荐：第一天解放碑、八一好吃街、洪崖洞，晚上去千厮门大桥拍照。
第二天山城步道、十八梯、白象居。第三天鹅岭二厂、李子坝、观音桥。
洪崖洞节假日人很多，建议晚上从桥上拍远景。
"""
    result = service.chat_json("note_extractor.md", text, NoteExtractionResult)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
