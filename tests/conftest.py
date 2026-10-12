import pytest
from tests.seed_test import trunc_db,seed_test_db,TestingSessionLocal

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