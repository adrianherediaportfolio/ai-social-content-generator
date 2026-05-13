import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.core.database import (
    delete_post,
    get_calendar,
    get_post,
    get_stats,
    list_posts,
    save_post,
    update_post,
)
from src.models.post import (
    GenerateRequest,
    GenerateResponse,
    PostDB,
    PostUpdate,
    ScheduleRequest,
    StatsResponse,
)
from src.services.generator import generate_posts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["content"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(req: GenerateRequest) -> GenerateResponse:
    """Generate social media content for multiple platforms."""
    posts = await generate_posts(
        topic=req.topic,
        source_url=req.source_url,
        platforms=req.platforms,
    )

    saved_posts = []
    for post in posts:
        await save_post(
            topic=req.topic,
            source_url=req.source_url,
            platform=post.platform,
            content=post.content,
            hashtags=post.hashtags,
        )
        post.character_count = len(post.content)
        saved_posts.append(post)

    return GenerateResponse(success=True, topic=req.topic, posts=saved_posts)


@router.get("/posts", response_model=list[PostDB])
async def get_posts(
    platform: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PostDB]:
    """List all posts with optional filters."""
    rows = await list_posts(platform=platform, status=status, limit=limit, offset=offset)
    return [PostDB(**row) for row in rows]


@router.get("/posts/{post_id}", response_model=PostDB)
async def get_post_by_id(post_id: int) -> PostDB:
    """Get a specific post by ID."""
    post = await get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostDB(**post)


@router.patch("/posts/{post_id}", response_model=PostDB)
async def update_post_endpoint(post_id: int, body: PostUpdate) -> PostDB:
    """Update a post's content, hashtags, status, or schedule."""
    existing = await get_post(post_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    await update_post(post_id, **updates)
    updated = await get_post(post_id)
    return PostDB(**updated)


@router.delete("/posts/{post_id}")
async def delete_post_endpoint(post_id: int) -> dict:
    """Delete a post."""
    deleted = await delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"success": True, "message": f"Post {post_id} deleted"}


@router.post("/posts/{post_id}/schedule", response_model=PostDB)
async def schedule_post(post_id: int, body: ScheduleRequest) -> PostDB:
    """Schedule a post for future publishing."""
    existing = await get_post(post_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        datetime.fromisoformat(body.scheduled_at)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO 8601.")

    await update_post(post_id, status="scheduled", scheduled_at=body.scheduled_at)
    updated = await get_post(post_id)
    return PostDB(**updated)


@router.get("/stats", response_model=StatsResponse)
async def get_dashboard_stats() -> StatsResponse:
    """Get dashboard statistics."""
    stats = await get_stats()
    return StatsResponse(**stats)


@router.get("/calendar")
async def get_content_calendar(year: int = 2026, month: int = 5) -> list[PostDB]:
    """Get posts for the content calendar view."""
    rows = await get_calendar(year, month)
    return [PostDB(**row) for row in rows]
