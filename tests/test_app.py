import pytest
import os
from app import app, BASE_DIR, DB_PATH

@pytest.fixture
def client():
    # Configure Flask for test mode
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test that the Home loads correctly (Status 200)"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"System Status" in response.data # Verify that the text is in the HTML

def test_logs_route(client):
    """Test that the logs route loads correctly"""
    response = client.get('/logs')
    assert response.status_code == 200

def test_database_creation():
    """Test that the database file exists after starting the app"""
    assert os.path.exists(DB_PATH)