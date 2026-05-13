import pytest
from httpx import ASGITransport, AsyncClient

from src.core.database import init_db
from src.main import app


@pytest.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("src.core.database.DB_PATH", db_path)
    await init_db()


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_content_without_openai():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/generate",
            json={"topic": "AI in education", "platforms": ["twitter", "linkedin"]},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["posts"]) == 2
    assert data["posts"][0]["platform"] == "twitter"
    assert data["posts"][1]["platform"] == "linkedin"


@pytest.mark.asyncio
async def test_list_posts_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/posts")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_post_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/posts/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stats_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "draft" in data


@pytest.mark.asyncio
async def test_generate_and_list_posts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/generate",
            json={"topic": "Test topic", "platforms": ["twitter"]},
        )
        response = await client.get("/api/v1/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) >= 1
    assert posts[0]["platform"] == "twitter"


@pytest.mark.asyncio
async def test_delete_post():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/generate",
            json={"topic": "Delete test", "platforms": ["twitter"]},
        )
        posts = await client.get("/api/v1/posts")
        post_id = posts.json()[0]["id"]
        response = await client.delete(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
