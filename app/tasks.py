from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.workers.packager import generate_package
from app.logger import logger


def package_idea_task(idea_id: int) -> None:
    """
    Runs packaging in a background context.
    IMPORTANT: create its own DB session (do NOT reuse request DB session).
    """
    db: Session = SessionLocal()
    try:
        package_idea(db, idea_id)
    except Exception:
        logger.error("Background packaging crashed", exc_info=True)
    finally:
        db.close()
