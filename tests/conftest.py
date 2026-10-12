import pytest
from tests.seed_test import trunc_db,seed_test_db,TestingSessionLocal
from main import app
from tests.common_methods import override_get_db
from database import get_db

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def db():
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def reset_database(db):
    trunc_db(db)
    seed_test_db(db)