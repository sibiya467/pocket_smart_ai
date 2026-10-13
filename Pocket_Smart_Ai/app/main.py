from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services import store
from app.routes import auth, api
from app.services.security import decode_token


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@app.on_event("startup")
def startup():
    store.init_db()


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    request.state.user_id = None

    token = request.cookies.get("access_token")

    if token:
        try:
            payload = decode_token(token)
            subject = payload.get("sub")
            request.state.user_id = int(subject)
        except (ValueError, TypeError, KeyError, Exception):
            request.state.user_id = None

    response = await call_next(request)
    return response


def render_page(request: Request, template_name: str, **context):
    """Render a Jinja2 template using the current Starlette API."""
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
    )


def require_login_page(request: Request):
    if not request.state.user_id:
        return RedirectResponse("/login", status_code=303)
    return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_page(request, "index.html", title="PocketSmart AI")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_page(request, "login.html", title="Login")


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render_page(request, "register.html", title="Register")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    redirect = require_login_page(request)
    if redirect:
        return redirect

    return render_page(request, "dashboard.html", title="Dashboard")


@app.get("/planner/{planner}", response_class=HTMLResponse)
def planner_page(planner: str, request: Request):

    redirect = require_login_page(request)
    if redirect:
        return redirect

    if planner not in {"home", "party", "jewelry"}:
        return HTMLResponse(
            "Planner not found",
            status_code=404
        )

    return render_page(
        request,
        f"{planner}_planner.html",
        title=f"{planner.title()} Planner"
    )


app.include_router(auth.router)
app.include_router(api.router)
