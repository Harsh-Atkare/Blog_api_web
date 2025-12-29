from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_get_posts_requires_auth():
    """Unauthenticated requests to list posts should be rejected"""
    resp = client.get("/posts")
    assert resp.status_code in (401, 403)


def test_get_post_requires_auth():
    """Unauthenticated requests to retrieve a post should be rejected"""
    resp = client.get("/posts/1")
    assert resp.status_code in (401, 403)
