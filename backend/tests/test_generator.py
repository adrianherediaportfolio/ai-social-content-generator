from src.services.generator import PLATFORM_SPECS, _generate_fallback


def test_fallback_twitter_within_limit():
    post = _generate_fallback("AI trends", "twitter")
    assert post.platform == "twitter"
    assert len(post.content) <= PLATFORM_SPECS["twitter"]["max_chars"]
    assert len(post.hashtags) > 0


def test_fallback_linkedin_within_limit():
    post = _generate_fallback("AI trends", "linkedin")
    assert post.platform == "linkedin"
    assert len(post.content) <= PLATFORM_SPECS["linkedin"]["max_chars"]


def test_fallback_instagram_within_limit():
    post = _generate_fallback("AI trends", "instagram")
    assert post.platform == "instagram"
    assert len(post.content) <= PLATFORM_SPECS["instagram"]["max_chars"]


def test_fallback_includes_topic():
    post = _generate_fallback("blockchain in healthcare", "twitter")
    assert "blockchain in healthcare" in post.content


def test_fallback_has_character_count():
    post = _generate_fallback("test topic", "twitter")
    assert post.character_count == len(post.content)
