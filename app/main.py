from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.workers.ideator import generate_ideas
from app.workers.packager import generate_package
from app.orchestrator import approve_idea, run_daily_generation
from fastapi import BackgroundTasks
from app.tasks import package_idea_task


from .db import engine, Base, get_db
from . import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    ideas = (
        db.query(models.Idea)
        .order_by(models.Idea.created_at.desc())
        .all()
    )
    for idea in ideas:
        idea.package = db.query(models.Package).filter(models.Package.idea_id == idea.id).first()
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "ideas": ideas}
        )

@app.get("/approve/{idea_id}")
def approve(idea_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ok = approve_idea(db, idea_id)

    if ok:
        # Run packaging asynchronously
        background_tasks.add_task(package_idea_task, idea_id)

    return RedirectResponse(url="/", status_code=303)


@app.get("/reject/{idea_id}")
def reject(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if idea:
        idea.status = "REJECTED"
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/generate")
def generate(db: Session = Depends(get_db)):
    run_daily_generation(db)
    return {"status": "AI ideas generated"}