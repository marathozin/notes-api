from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    emoji: str = Field(..., min_length=1, max_length=10)


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    model_config = {"from_attributes": True}
