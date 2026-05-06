from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "ok"
    data: Optional[T] = None


def ok(data=None, message: str = "ok") -> dict:
    return {"success": True, "message": message, "data": data}


def fail(message: str, data=None) -> dict:
    return {"success": False, "message": message, "data": data}
