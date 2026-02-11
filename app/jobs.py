from app.db import SessionLocal
from app.orchestrator import run_agent_cycle
from app.logger import logger


def agent_cycle_job():
    """
    Entry point for RQ worker to run full agent cycle.
    """

    db = SessionLocal()

    try:
        run_agent_cycle(db)
    except Exception:
        logger.error("Agent cycle crashed", exc_info=True)
    finally:
        db.close()
