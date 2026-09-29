from typing import Literal

from pydantic import BaseModel, Field, EmailStr


PlannerType = Literal[
    "home",
    "party",
    "jewelry"
]


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: list[str] = Field(min_length=1)
    style: str = Field(min_length=2, max_length=100)
    items: dict[str, int] = Field(default_factory=dict)
    notes: str = ""


class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=100000)
    event_type: str = Field(min_length=2, max_length=100)
    venue: str = ""
    preferences: str = ""


class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: float
    platform: str
    url: str = ""
    reason: str
    quantity: int = 1


class RecommendationResponse(BaseModel):
    planner: PlannerType
    summary: str
    budget: float
    allocated_total: float
    items: list[RecommendationItem]
    tips: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Prices and availability are estimates and "
        "should be checked on the provider before purchase."
    )


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(min_length=2, max_length=100)
    outfit_description: str = ""
    preferences: str = ""
