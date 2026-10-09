import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, Base, get_db

@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        with Session() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()

def test_crud(client):
    created = client.post('/tasks', json={'title':'Write tests'})
    assert created.status_code == 201
    task_id = created.json()['id']
    assert client.get(f'/tasks/{task_id}').json()['title'] == 'Write tests'
    assert len(client.get('/tasks?status=todo').json()) == 1
    assert client.patch(f'/tasks/{task_id}', json={'status':'done'}).json()['status'] == 'done'
    assert client.delete(f'/tasks/{task_id}').status_code == 204
    assert client.get(f'/tasks/{task_id}').status_code == 404

def test_validation(client):
    assert client.post('/tasks', json={'title':''}).status_code == 422
    assert client.get('/tasks?limit=0').status_code == 422
