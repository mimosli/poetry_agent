from sqlalchemy.orm import Session

from app import models
from app.workers.ideator import generate_ideas
from app.workers.packager import generate_package
from app.logger import logger


def run_daily_generation(db: Session):
    try:
        generate_ideas(db)
    except Exception:
        logger.error("Daily generation failed", exc_info=True)


def approve_idea(db: Session, idea_id: int) -> bool:
    """
    Only marks APPROVED. Returns True if approved, False otherwise.
    """
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        return False

    if idea.status not in ["PROPOSED", "CREATED"]:
        return False

    idea.status = "APPROVED"
    db.commit()
    return True


def package_idea(db: Session, idea_id: int) -> None:
    """
    Does the packaging workflow (meant to run in background).
    """
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not idea:
        return

    # Idempotency: if already done, do nothing
    if idea.status == "PACKAGED":
        return

    try:
        idea.status = "PACKAGING"
        db.commit()

        generate_package(db, idea_id)

        # generate_package may already set PACKAGED, but we enforce final state
        idea.status = "PACKAGED"
        db.commit()

    except Exception:
        idea.status = "FAILED"
        db.commit()
        logger.error("Packaging failed", exc_info=True)
