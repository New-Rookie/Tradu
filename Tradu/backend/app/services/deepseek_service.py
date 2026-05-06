from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

load_dotenv()

T = TypeVar("T", bound=BaseModel)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = BACKEND_ROOT / "app" / "prompts"


class DeepSeekService:
    def __init__(self) -> None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("Missing DEEPSEEK_API_KEY in .env")

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @staticmethod
    def load_prompt(prompt_name: str) -> str:
        path = PROMPT_DIR / prompt_name
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    def chat_json(
        self,
        prompt_name: str,
        user_input: str,
        schema_cls: Type[T],
        max_tokens: int = 2048,
        retry: int = 1,
    ) -> T:
        system_prompt = self.load_prompt(prompt_name)
        last_error: Exception | None = None

        for attempt in range(retry + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=max_tokens,
                    temperature=0.2,
                )
                content = response.choices[0].message.content or ""
                if not content.strip():
                    raise ValueError("DeepSeek returned empty content")
                data: Dict[str, Any] = json.loads(content)
                return schema_cls.model_validate(data)
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                last_error = exc
                user_input = (
                    "上一次输出不符合要求。请只输出严格合法的 json，"
                    "不要输出 Markdown、解释或代码块。原始输入如下：\n" + user_input
                )

        raise RuntimeError(f"DeepSeek structured output failed: {last_error}")
