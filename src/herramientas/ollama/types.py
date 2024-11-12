from typing_extensions import TypedDict
from typing import Optional
from fundar_llms._types import Base64, Context # type: ignore

class OllamaArgs(TypedDict, total=False):
    model: str
    prompt: str
    raw: Optional[bool]
    image: Optional[Base64]
    suffix: Optional[str]
    format: Optional[str]
    system: Optional[str]
    context: Optional[Context]
    stream: Optional[bool]
    num_ctx: Optional[int]
    num_predict: Optional[int]
    temperature: Optional[float]
    top_k: Optional[int]
    top_p: Optional[float]