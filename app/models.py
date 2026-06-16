"""
Pydantic models for the Item resource - a cupboard/pantry stock tracker.

Same shape as the earlier Case model, renamed and re-purposed: a thing
with a name, a category, and a status.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Your three states: In Stock, Low in Stock, Out of Stock.
# Literal does double duty here - it's the type AND the validation rule.
ItemStatus = Literal["in_stock", "low_stock", "out_of_stock"]


class Item(BaseModel):
    """A cupboard item as stored and returned by the API."""

    id: str
    name: str
    category: str
    status: ItemStatus
    created_at: str
    updated_at: str


class CreateItemDto(BaseModel):
    """Request body shape for POST /items."""

    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    status: ItemStatus = "in_stock"


class UpdateItemDto(BaseModel):
    """Request body shape for PATCH /items/{id}."""

    name: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1)
    status: Optional[ItemStatus] = None
