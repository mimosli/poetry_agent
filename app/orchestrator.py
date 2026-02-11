from sqlalchemy.orm import Session

from app import models
from app.agent import PoetryAgent
from app.workers.ideator import generate_ideas
from app.workers.packager import generate_package
from app.logger import logger


def build_state_description(db: Session) -> str:
    approved = db.query(models.Idea).filter(models.Idea.status == "APPROVED").all()
    proposed = db.query(models.Idea).filter(models.Idea.status == "PROPOSED").all()
    packaged = db.query(models.Idea).filter(models.Idea.status == "PACKAGED").all()

    return f"""
Approved ideas: {[i.id for i in approved]}
Proposed ideas: {[i.id for i in proposed]}
Packaged ideas: {[i.id for i in packaged]}
"""


def execute_action(db: Session, action: str) -> bool:
    """
    Executes agent decision.
    Returns True if action was executed, False if loop should stop.
    """

    if action == "generate_ideas":
        generate_ideas(db)
        return True

    if action == "package_idea":
        approved = db.query(models.Idea).filter(models.Idea.status == "APPROVED").all()
        if approved:
            generate_package(db, approved[0].id)
            return True
        return False

    if action == "wait":
        logger.info("Agent decided to wait.")
        return False

    logger.warning(f"Unknown action received: {action}")
    return False


def run_agent_cycle(db: Session, max_steps: int = 3):
    """
    Controlled OpenClaw-style reasoning loop.
    """

    agent = PoetryAgent(db)

    for step in range(max_steps):

        state_description = build_state_description(db)
        decision = agent.think(state_description)

        action = decision.get("action")

        logger.info(f"Step {step + 1} decision: {decision}")

        should_continue = execute_action(db, action)

        if not should_continue:
            break
