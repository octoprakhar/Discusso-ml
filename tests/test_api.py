from fastapi.testclient import TestClient
from app.main import app

## Creating a client: It is for me a fake browser, where I will test
client = TestClient(app)

## Integration Testing
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}