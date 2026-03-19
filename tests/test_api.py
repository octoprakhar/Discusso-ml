import os

from fastapi.testclient import TestClient
from app.main import app

## Creating a client: It is for me a fake browser, where I will test
client = TestClient(app)
TEST_SECRET = os.getenv("ML_INTERNAL_SECRET")

## Integration Testing
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}


## Testing whether my tag generation hit the background task or not

def test_tag_endpoint_success(mocker):
    mock_db = mocker.patch("app.api.routes.process_tagging")

    ## Fake request
    payload = {
        "post_id": "123-abc",
        "title": "Learning PyTest",
        "description":"This is a test description"
    }

    ## Need to include fake secret
    response = client.post(
        "/tag", 
        json=payload,
        headers={"x-internal-secret": TEST_SECRET} 
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}

    ## Was the background logic triggered?
    mock_db.assert_called_once()