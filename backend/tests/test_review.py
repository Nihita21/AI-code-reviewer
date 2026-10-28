from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_review_detects_real_issues():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": (
                "import os\n"
                "def greet(names=[]):\n"
                "    try:\n"
                "        print(names)\n"
                "    except Exception:\n"
                "        pass\n"
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()
    titles = [issue["title"] for issue in result["issues"]]

    assert result["score"] == 65
    assert "Unused import: os" in titles
    assert "Mutable default argument: names" in titles
    assert "Empty exception handler" in titles


def test_review_clean_code():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "def greet(name):\n    return f'Hello, {name}'",
        },
    )

    assert response.status_code == 200
    assert response.json()["score"] == 100
    assert response.json()["issues"] == []


def test_review_syntax_error():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "def greet(:",
        },
    )

    assert response.status_code == 200
    assert response.json()["issues"][0]["severity"] == "high"


def test_review_rejects_empty_code():
    response = client.post(
        "/review",
        json={
            "language": "python",
            "code": "   ",
        },
    )

    assert response.status_code == 400


def test_review_rejects_unsupported_language():
    response = client.post(
        "/review",
        json={
            "language": "javascript",
            "code": "console.log('Hello')",
        },
    )

    assert response.status_code == 400
