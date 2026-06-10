from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.agents.ats_agent import ATSEvaluatorAgent
from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.jd_agent import JDAnalyzerAgent
from app.agents.profile_agent import ProfileAgent
from app.agents.resume_agent import ResumeStrategistAgent
from app.config import APP_DIR, GENERATED_DIR
from app.services.pdf_service import PDFService
from app.services.profile_store import ProfileStore


router = APIRouter()
templates = Jinja2Templates(directory=APP_DIR / "templates")


class GenerateRequest(BaseModel):
    job_description: str = Field(..., min_length=40)
    company_name: str | None = None
    role_title: str | None = None
    refresh_profile: bool = False


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/api/profile/refresh")
async def refresh_profile():
    profile = await ProfileAgent().refresh_profile()
    return {"status": "updated", "profile": profile}


@router.post("/api/generate")
async def generate_documents(payload: GenerateRequest, background_tasks: BackgroundTasks):
    profile_store = ProfileStore()
    profile = (
        await ProfileAgent().refresh_profile()
        if payload.refresh_profile
        else profile_store.load()
    )

    jd_agent = JDAnalyzerAgent()
    resume_agent = ResumeStrategistAgent()
    cover_agent = CoverLetterAgent()
    ats_agent = ATSEvaluatorAgent()
    pdf_service = PDFService()

    jd_analysis = await jd_agent.analyze(payload.job_description)
    resume_strategy = await resume_agent.build_resume(
        profile=profile,
        job_description=payload.job_description,
        jd_analysis=jd_analysis,
        role_title=payload.role_title,
    )
    evaluation = await ats_agent.evaluate(
        profile=profile,
        resume=resume_strategy,
        jd_analysis=jd_analysis,
    )
    cover_letter = await cover_agent.write(
        profile=profile,
        job_description=payload.job_description,
        jd_analysis=jd_analysis,
        company_name=payload.company_name,
        role_title=payload.role_title,
    )

    request_id = uuid4().hex[:12]
    resume_filename = f"resume_{request_id}.pdf"
    cover_filename = f"cover_letter_{request_id}.pdf"
    resume_path = GENERATED_DIR / resume_filename
    cover_path = GENERATED_DIR / cover_filename

    pdf_service.render_resume(
        resume_strategy=resume_strategy,
        jd_analysis=jd_analysis,
        evaluation=evaluation,
        output_path=resume_path,
    )
    pdf_service.render_cover_letter(
        cover_letter=cover_letter,
        profile=profile,
        company_name=payload.company_name,
        role_title=payload.role_title,
        output_path=cover_path,
    )

    background_tasks.add_task(pdf_service.prune_old_files)

    return {
        "match_score": evaluation["score"],
        "matched_skills": evaluation["matched_skills"],
        "missing_skills": evaluation["missing_skills"],
        "keywords": jd_analysis.get("keywords", []),
        "feedback": evaluation.get("feedback", []),
        "resume_url": f"/download/{resume_filename}",
        "cover_letter_url": f"/download/{cover_filename}",
    }


@router.get("/download/{filename}")
async def download(filename: str):
    path = (GENERATED_DIR / filename).resolve()
    if GENERATED_DIR.resolve() not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, filename=filename, media_type="application/pdf")

