import os
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session

from app import models
from app.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_package(db: Session, idea_id: int):
    idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if idea.status == "PACKAGED":
        return
    prompt = f"""
You are creating a full Instagram Reel content package for a modern poetry book.

Idea:
Title: {idea.title}
Hook: {idea.hook}
Format: {idea.format}
Objective: {idea.objective}

Generate:

1. Full 15-second script (spoken or text overlay)
2. Scene-by-scene structure (timestamped)
3. Caption optimized for Instagram
4. 8 relevant hashtags
5. Soft CTA to read the poetry book (link in bio)

Tone: emotional, poetic, modern.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create viral Instagram poetry reels."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )

    content = response.choices[0].message.content

    # Create folder
    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = f"content/{today}/idea_{idea.id}"
    os.makedirs(folder_path, exist_ok=True)

    # Save files
    with open(f"{folder_path}/package.txt", "w", encoding="utf-8") as f:
        f.write(content)

    # Save to DB
    package = models.Package(
        idea_id=idea.id,
        folder_path=folder_path
    )

    idea.status = "PACKAGED"

    db.add(package)
    db.commit()
