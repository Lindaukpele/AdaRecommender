from fastapi import FastAPI
from fastapi.responses import Response
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from contextlib import asynccontextmanager
import os

# 🔹 Neon Postgres connection string
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://neondb_owner:npg_LN0caK9xfCTl@ep-crimson-sky-ad4jbazk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require" 
)

engine = create_engine(DATABASE_URL, echo=True)


# 🔹 Map to the existing "users" table
class User(SQLModel, table=True):
    __tablename__ = "users"   # 👈 force SQLModel to use your existing table
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    agency: str
    location: str
    genres: str
    website: str


def create_db_and_tables():
    # Don’t recreate the table if it already exists
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# 🔹 Routes
@app.get("/")
def root():
    return {"message": "Welcome to AdaAnalytics Users API"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)  # no content

@app.post("/users/")
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.get("/users/", response_model=List[User])
def read_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users