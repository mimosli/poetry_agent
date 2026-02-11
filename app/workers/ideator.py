import json
from openai import OpenAI
from sqlalchemy.orm import Session

from app import models
from app.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_ideas(db: Session):
    prompt = """
You are a viral Instagram Reel strategist for a modern poetry book.

Generate 3 faceless Instagram Reel ideas.

Each idea must include:
- title
- hook (emotionally powerful, 1–2 lines)
- format (short description of visual style)
- objective (Followers / Saves / Traffic)

Tone: emotional, modern, slightly melancholic.

Return ONLY valid JSON in this format:
[
  {
    "title": "...",
    "hook": "...",
    "format": "...",
    "objective": "..."
  }
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create viral Instagram poetry content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    content = response.choices[0].message.content.strip()

    try:
        ideas = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"AI did not return valid JSON:\n{content}")

    for idea_data in ideas:
        idea = models.Idea(
            title=idea_data["title"],
            hook=idea_data["hook"],
            format=idea_data["format"],
            objective=idea_data["objective"],
            status="PROPOSED"
        )
        db.add(idea)

    db.commit()
