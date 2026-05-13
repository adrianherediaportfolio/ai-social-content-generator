import json
import logging
import re

from openai import AsyncOpenAI

from src.core.config import settings
from src.models.post import PostContent

logger = logging.getLogger(__name__)

PLATFORM_SPECS = {
    "twitter": {
        "name": "Twitter/X",
        "max_chars": 280,
        "style": "concise, punchy, engaging. Use 2-3 relevant hashtags. Include a call to action.",
    },
    "linkedin": {
        "name": "LinkedIn",
        "max_chars": 3000,
        "style": (
            "professional, insightful, thought-leadership tone. "
            "Start with a hook. Use line breaks for readability. "
            "Include 3-5 relevant hashtags at the end."
        ),
    },
    "instagram": {
        "name": "Instagram",
        "max_chars": 2200,
        "style": (
            "engaging, visual-friendly caption. Start with a strong hook. "
            "Use emojis strategically. Include 15-20 highly relevant hashtags "
            "at the end, mixing popular and niche tags."
        ),
    },
}

GENERATION_PROMPT = """You are a social media content expert. \
Generate a post for {platform_name} about the following topic.

Topic: {topic}
{url_context}

Platform requirements:
- Maximum {max_chars} characters
- Style: {style}

Return a JSON object with these fields:
- "content": the post text (within character limit)
- "hashtags": array of hashtag strings (without the # symbol)

Return ONLY valid JSON, no markdown formatting."""


async def generate_posts(topic: str, source_url: str, platforms: list[str]) -> list[PostContent]:
    if not settings.openai_api_key:
        logger.warning("No OpenAI API key, using template fallback")
        return [_generate_fallback(topic, p) for p in platforms]

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    results = []

    for platform in platforms:
        spec = PLATFORM_SPECS.get(platform)
        if not spec:
            logger.warning(f"Unknown platform: {platform}, skipping")
            continue

        url_context = f"Source URL for reference: {source_url}" if source_url else ""
        prompt = GENERATION_PROMPT.format(
            platform_name=spec["name"],
            topic=topic,
            url_context=url_context,
            max_chars=spec["max_chars"],
            style=spec["style"],
        )

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You generate social media content. Return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\n?", "", content)
                content = re.sub(r"\n?```$", "", content)

            data = json.loads(content)
            post = PostContent(
                platform=platform,
                content=data.get("content", ""),
                hashtags=data.get("hashtags", []),
                character_count=len(data.get("content", "")),
            )
            results.append(post)

        except Exception as e:
            logger.error(f"AI generation failed for {platform}: {e}")
            results.append(_generate_fallback(topic, platform))

    return results


def _generate_fallback(topic: str, platform: str) -> PostContent:
    """Template-based fallback when OpenAI is not available."""
    templates = {
        "twitter": (
            f"Exploring {topic} — the future is here. "
            "What are your thoughts? #tech #innovation"
        ),
        "linkedin": (
            f"I've been diving deep into {topic} and wanted to share some thoughts.\n\n"
            f"The landscape is changing rapidly, and businesses that adapt early "
            f"will have a significant advantage.\n\n"
            f"Key takeaways:\n"
            f"- Innovation is accelerating\n"
            f"- Early adopters win\n"
            f"- The time to act is now\n\n"
            f"What's your experience with {topic}? I'd love to hear your perspective.\n\n"
            f"#technology #innovation #business"
        ),
        "instagram": (
            f"The future of {topic} is incredible.\n\n"
            f"We're seeing amazing developments that will transform how we work "
            f"and live. Stay ahead of the curve.\n\n"
            f"Double tap if you agree! What excites you most about this?\n\n"
            f"#tech #innovation #future #technology #digital #trending"
        ),
    }
    content = templates.get(platform, templates["twitter"])
    hashtags = ["tech", "innovation", "business", "trending"]
    return PostContent(
        platform=platform,
        content=content,
        hashtags=hashtags,
        character_count=len(content),
    )
