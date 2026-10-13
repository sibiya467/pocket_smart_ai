from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.models.schemas import RegisterRequest, LoginRequest
from app.services import store
from app.services.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter()


@router.post("/register")
def register(data: RegisterRequest):
    name = data.name.strip()
    email = data.email.strip().lower()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Name must contain at least 2 characters."
        )

    existing_user = store.get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered."
        )

    user_id = store.create_user(
        name,
        email,
        hash_password(data.password)
    )

    return {
        "message": "Registration successful",
        "user_id": user_id
    }


@router.post("/login")
def login(data: LoginRequest):
    email = data.email.strip().lower()

    user = store.get_user_by_email(email)

    if not user or not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    response = RedirectResponse(
        "/dashboard",
        status_code=303
    )

    token = create_access_token(str(user["id"]))

    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        path="/"
    )

    return response


@router.post("/token")
def token(data: LoginRequest):
    email = data.email.strip().lower()

    user = store.get_user_by_email(email)

    if not user or not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "access_token": create_access_token(
            str(user["id"])
        ),
        "token_type": "bearer"
    }


@router.post("/logout")
def logout():
    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.delete_cookie(
        "access_token",
        path="/"
    )

    return response
