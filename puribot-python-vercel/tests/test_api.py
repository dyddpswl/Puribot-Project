from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_health():
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['question_count'] == 20

def test_questions():
    r = client.get('/api/questions?q=26010-0001')
    assert r.status_code == 200
    assert r.json()[0]['id'] == '26010-0001'

def test_hint_without_api_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    r = client.post('/api/coach', json={'question_id':'26010-0001','mode':'hint','hint_level':1})
    assert r.status_code == 200
    assert r.json()['source'] == '기본 안내'

def test_invalid_id():
    assert client.get('/api/questions/not-found').status_code == 404
