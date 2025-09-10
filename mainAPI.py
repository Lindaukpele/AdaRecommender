from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from contextlib import asynccontextmanager

# 🔹 Neon Postgres connection string
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_LN0caK9xfCTl@ep-crimson-sky-ad4jbazk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

# 🔹 Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)


# 🔹 Define model
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    agency: str
    location: str
    genres: str
    website: str


# 🔹 Create tables if they don’t exist
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 🔹 FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# 🔹 Routes

@app.get("/")
def root():
    return {"message": "Welcome to the Item API"}


@app.post("/items/")
def create_item(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.get("/items/", response_model=List[Item])
def read_items():
    with Session(engine) as session:
        items = session.exec(select(Item)).all()
        return items