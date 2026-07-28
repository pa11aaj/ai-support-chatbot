from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        ..., description="Full conversation so far, oldest message first."
    )


class ChatResponse(BaseModel):
    reply: str
    used_tools: List[str] = Field(
        default_factory=list,
        description="Names of backend tools the model invoked to answer "
        "(e.g. get_order_status, get_product_info). Useful for debugging/demo purposes.",
    )


class EscalationRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    summary: str
