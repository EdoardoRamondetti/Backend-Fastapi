from models import User,Post,Base
from security import password_hash
from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)

def seed_test_db(db):
    andrea = User(name="Andrea",email="andrea@test.com",password_hash=password_hash.hash("password123"),role="admin")
    antonio = User(name="Antonio",email="antonio@gmail.com",password_hash=password_hash.hash("password123"),role="user")
    luca = User(name="Luca",email="luca@example.com",password_hash=password_hash.hash("password123"),role="user")

    db.add_all([andrea, antonio, luca])
    db.commit()

    post1 = Post(title="post1",content="contenuto", user=andrea)
    post2 = Post(title="marketing",content="il marketing serve", user_id=2)
    post3 = Post(title="post3",content="contenuto", user=andrea)
    post4 = Post(title="post4",content="contenuto", user=andrea)
    post5 = Post(title="post5",content="contenuto", user=andrea)
    post6 = Post(title="Come scrivere backend con python",content="Si utilizza Fastapi", user=antonio)
    post7 = Post(title="Come imparare a programmare con python",content="come farlo", user=antonio)
    post8 = Post(title="Come scrivere un for in python",content="contenuto", user=antonio)

    db.add_all([post1, post2,post3,post4,post5,post6,post7,post8])
    db.commit()

def trunc_db(db):
    db.query(Post).delete()
    db.query(User).delete()

    db.commit()