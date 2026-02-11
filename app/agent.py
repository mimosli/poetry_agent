from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.logger import logger
import json


client = OpenAI(api_key=OPENAI_API_KEY)


class PoetryAgent:

    def think(self, state_description: str):
        prompt = f"""
You are an autonomous content operator for a modern poetry Instagram account.

Current system state:
{state_description}

Available tools:
- generate_ideas
- package_idea
- wait

Rules:
- If there are APPROVED ideas → package them.
- If there are no ideas today → generate ideas.
- Otherwise → wait.

Respond ONLY with valid JSON:

{{
    "action": "generate_ideas | package_idea | wait",
    "idea_id": optional integer,
    "reason": "short explanation"
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict JSON decision engine."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Agent returned invalid JSON")
            return {"action": "wait", "reason": "invalid JSON"}
