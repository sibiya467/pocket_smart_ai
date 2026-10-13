import json
import sqlite3

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile
)

from app.models.schemas import (
    HomeRequest,
    PartyRequest,
    JewelryRequest
)

from app.services import store

from app.services.recommender import generate


router = APIRouter()


def get_user(user_id):

    with sqlite3.connect(
        store.DB_PATH
    ) as connection:

        connection.row_factory = sqlite3.Row

        return connection.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        ).fetchone()


def current_user(request: Request):

    user_id = request.state.user_id

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in first."
        )

    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user


@router.post("/generate-home")
def generate_home(
    data: HomeRequest,
    request: Request
):

    user = current_user(request)

    result = generate(
        "home",
        data.model_dump()
    )

    history_id = store.save_history(
        user["id"],
        "home",
        data.model_dump(),
        result.model_dump()
    )

    return {
        "history_id": history_id,
        **result.model_dump()
    }


@router.post("/generate-party")
def generate_party(
    data: PartyRequest,
    request: Request
):

    user = current_user(request)

    result = generate(
        "party",
        data.model_dump()
    )

    history_id = store.save_history(
        user["id"],
        "party",
        data.model_dump(),
        result.model_dump()
    )

    return {
        "history_id": history_id,
        **result.model_dump()
    }


@router.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(...),
    outfit_description: str = Form(""),
    preferences: str = Form(""),
    outfit_image: UploadFile | None = File(None)
):

    user = current_user(request)

    data = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        outfit_description=outfit_description,
        preferences=preferences
    )

    image_bytes = None
    image_type = "image/jpeg"

    if outfit_image and outfit_image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif"
        }

        if outfit_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image type. Use JPEG, PNG, WEBP, or GIF."
            )

        image_bytes = await outfit_image.read()

        # Keep uploads reasonably small for local/API processing.
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Image is too large. Maximum size is 10 MB."
            )

        image_type = outfit_image.content_type

    result = generate(
        "jewelry",
        data.model_dump(),
        image_bytes,
        image_type
    )

    history_id = store.save_history(
        user["id"],
        "jewelry",
        data.model_dump(),
        result.model_dump()
    )

    return {
        "history_id": history_id,
        **result.model_dump()
    }


@router.get("/history")
def history(request: Request):

    user = current_user(request)

    rows = store.list_history(
        user["id"]
    )

    for row in rows:

        row["request"] = json.loads(
            row.pop("request_json")
        )

        row["response"] = json.loads(
            row.pop("response_json")
        )

    return rows


@router.get(
    "/recommendations-details/{history_id}"
)
def recommendation_details(
    history_id: int,
    request: Request
):

    user = current_user(request)

    row = store.get_history(
        user["id"],
        history_id
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found."
        )

    return json.loads(
        row["response_json"]
    )


@router.get("/session-info")
def session_info(request: Request):

    user = current_user(request)

    return {
        "logged_in": True,
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }


@router.get("/session-data")
def session_data(request: Request):

    user = current_user(request)

    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        },
        "history": store.list_history(
            user["id"]
        )
    }


@router.get("/health")
def health():

    return {
        "status": "ok"
    }