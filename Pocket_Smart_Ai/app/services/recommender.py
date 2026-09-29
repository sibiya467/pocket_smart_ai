import json

from pydantic import BaseModel

from google import genai

from app.config import settings

from app.models.schemas import (
    RecommendationResponse,
    RecommendationItem
)


class AIRecommendation(BaseModel):

    summary: str

    budget: float

    allocated_total: float

    items: list[
        RecommendationItem
    ]

    tips: list[str] = []


def build_prompt(
    planner,
    data
):

    return f"""
You are PocketSmart AI.

You are a budget-aware recommendation assistant.

Planner:
{planner}

User information:
{json.dumps(data, indent=2)}

Your task is to generate useful recommendations
that fit the user's budget.

Important rules:

1. Stay within the user's stated budget.
2. Give practical recommendations.
3. Do not claim that a product is currently
   available unless live product data is provided.
4. Do not invent live prices.
5. Treat platform names as suggested destinations.
6. Keep the response concise.
7. Give approximately 5 to 8 recommendations.
8. Include quantity where appropriate.
9. Return valid structured JSON.
"""


def generate(
    planner,
    data,
    image_bytes=None,
    mime_type="image/jpeg"
):

    if (
        settings.use_mock_ai
        or not settings.gemini_api_key
    ):

        return mock_recommendation(
            planner,
            data
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    contents = [
        build_prompt(
            planner,
            data
        )
    ]

    if image_bytes:

        contents.append(
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
            }
        )

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_schema": AIRecommendation
        }
    )

    parsed = getattr(
        response,
        "parsed",
        None
    )

    if isinstance(
        parsed,
        AIRecommendation
    ):

        result = parsed

    elif parsed is not None:

        result = (
            AIRecommendation
            .model_validate(parsed)
        )

    else:

        result = (
            AIRecommendation
            .model_validate_json(
                response.text
            )
        )

    return RecommendationResponse(
        planner=planner,
        disclaimer=(
            RecommendationResponse
            .model_fields["disclaimer"]
            .default
        ),
        **result.model_dump()
    )


def mock_recommendation(
    planner,
    data
):

    budget = float(
        data["budget"]
    )

    recommendation_groups = {

        "home": [

            (
                "LED ceiling light",
                "Lighting",
                0.10,
                "Amazon"
            ),

            (
                "Compact storage cabinet",
                "Storage",
                0.22,
                "IKEA"
            ),

            (
                "Decorative wall art",
                "Decor",
                0.10,
                "Flipkart"
            ),

            (
                "Ceiling fan",
                "Utility",
                0.22,
                "Amazon"
            ),

            (
                "Dining table",
                "Furniture",
                0.28,
                "IKEA"
            )
        ],

        "party": [

            (
                "Catering package",
                "Food",
                0.40,
                "Swiggy"
            ),

            (
                "Decoration package",
                "Decor",
                0.15,
                "Zomato"
            ),

            (
                "Venue option",
                "Venue",
                0.25,
                "OYO"
            ),

            (
                "Entertainment",
                "Entertainment",
                0.12,
                "Local vendor"
            )
        ],

        "jewelry": [

            (
                "Minimal necklace set",
                "Necklace",
                0.25,
                "Amazon"
            ),

            (
                "Matching earrings",
                "Earrings",
                0.12,
                "Flipkart"
            ),

            (
                "Bracelet",
                "Bracelet",
                0.10,
                "Amazon"
            ),

            (
                "Hair accessory",
                "Accessory",
                0.06,
                "Flipkart"
            )
        ]
    }

    selected = recommendation_groups[
        planner
    ]

    recommendations = []

    for (
        name,
        category,
        percentage,
        platform
    ) in selected:

        recommendations.append(
            RecommendationItem(
                name=name,
                category=category,
                estimated_price=round(
                    budget * percentage,
                    2
                ),
                platform=platform,
                reason=(
                    "Budget-friendly "
                    "placeholder recommendation."
                ),
                quantity=1
            )
        )

    total = round(
        sum(
            item.estimated_price
            * item.quantity
            for item in recommendations
        ),
        2
    )

    return RecommendationResponse(
        planner=planner,
        summary=(
            "Mock recommendations are enabled. "
            "Add a Gemini API key for AI-generated results."
        ),
        budget=budget,
        allocated_total=total,
        items=recommendations,
        tips=[
            "Verify current price and availability before purchase.",
            "Adjust quantities to keep the final total within budget."
        ]
    )