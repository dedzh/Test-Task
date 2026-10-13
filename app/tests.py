import os
import pytest

os.environ.setdefault("ES_HOST", "http://localhost:9200")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app import app as flask_app, db, es  # noqa: E402
from app.models import Docs  # noqa: E402
from app.elastic import add_to_index, ensure_index  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def clean_es():
    """Удаляем индекс перед всеми тестами и после."""
    if es.indices.exists(index="docs"):
        es.indices.delete(index="docs")
    ensure_index("docs")
    yield
    if es.indices.exists(index="docs"):
        es.indices.delete(index="docs")


@pytest.fixture
def client():
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def seed_db():
    """Перед каждым тестом — чистая БД + индекс с 3 документами."""
    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        docs = [
            Docs(id=1, text="святой источник", raw_created_date="2019-01-01 10:00:00", rubrics="['a']"),
            Docs(id=2, text="святой воин", raw_created_date="2019-02-01 10:00:00", rubrics="['b']"),
            Docs(id=3, text="админам привет", raw_created_date="2019-03-01 10:00:00", rubrics="['c']"),
        ]
        db.session.add_all(docs)
        db.session.commit()

        if es.indices.exists(index="docs"):
            es.indices.delete(index="docs")
        ensure_index("docs")
        for d in docs:
            add_to_index("docs", d)
        es.indices.refresh(index="docs")

        yield

        db.session.remove()
        db.drop_all()


def test_delete_existing(client):
    r = client.delete("/delete/?id=1")
    assert r.status_code == 200
    assert r.data.decode() == "True"


def test_delete_not_found(client):
    r = client.delete("/delete/?id=99999")
    assert r.data.decode() == "Not found post with such id"


def test_delete_invalid_id(client):
    r = client.delete("/delete/?id=abc")
    assert r.data.decode() == "Not found post with such id"


def test_search_returns_results(client):
    r = client.get("/search/?text=святой")
    assert r.status_code == 200
    data = r.get_json()
    ids = [d["id"] for d in data]
    assert 1 in ids and 2 in ids


def test_search_empty(client):
    r = client.get("/search/?text=")
    assert r.status_code == 200
    assert r.get_json() == []


def test_search_after_delete(client):
    client.delete("/delete/?id=1")
    r = client.get("/search/?text=святой")
    ids = [d["id"] for d in r.get_json()]
    assert 1 not in ids
    assert 2 in ids


def test_search_sorted_by_created_date_desc(client):
    r = client.get("/search/?text=святой")
    dates = [d["created_date"] for d in r.get_json()]
    assert dates == sorted(dates, reverse=True)