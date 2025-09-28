from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator
from typing import Literal

class AssistantResponse(BaseModel):
    type: Literal["command", "waifu"] = Field(
        ..., description="The type of response"
    )
    content: str = Field(..., description="The content of the response")
    comment: str | None = Field(..., description="The comment for the response")
    dangerous: Literal["1", "0"] | None = Field(
        "0", description="Indicates if the command is dangerous ('1' for yes, '0' for no)" 
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value, info):
        if info.data.get("type") == "confirm" and value not in ["1", "0"]:
            raise ValueError("Confirm type must have content '1' or '0'")
        return value