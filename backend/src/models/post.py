from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="Topic or description")
    source_url: str = Field(default="", description="Optional URL for context")
    platforms: list[str] = Field(
        default=["twitter", "linkedin", "instagram"],
        description="Target platforms",
    )


class PostContent(BaseModel):
    platform: str
    content: str
    hashtags: list[str] = Field(default_factory=list)
    character_count: int = 0


class GenerateResponse(BaseModel):
    success: bool
    topic: str
    posts: list[PostContent]


class PostDB(BaseModel):
    id: int
    topic: str
    source_url: str = ""
    platform: str
    content: str
    hashtags: list[str] = Field(default_factory=list)
    status: str = "draft"
    scheduled_at: str | None = None
    published_at: str | None = None
    created_at: str = ""
    updated_at: str = ""


class PostUpdate(BaseModel):
    content: str | None = None
    hashtags: list[str] | None = None
    status: str | None = None
    scheduled_at: str | None = None


class ScheduleRequest(BaseModel):
    scheduled_at: str = Field(..., description="ISO 8601 datetime for scheduling")


class StatsResponse(BaseModel):
    total: int
    draft: int
    scheduled: int
    published: int
