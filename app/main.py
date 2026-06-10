from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import APP_DIR, GENERATED_DIR


GENERATED_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI Resume Builder",
    description="Tailored resume and cover letter generator powered by Mistral.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.include_router(router)

