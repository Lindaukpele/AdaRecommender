from fastapi import FastAPI, Query, HTTPException
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


@app.get("/users/")
def read_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        # Reorder fields so id is first
        result = [
            {
                "id": user.id,
                "name": user.name,
                "agency": user.agency,
                "location": user.location,
                "genres": user.genres,
                "website": user.website
            }
            for user in users
        ]
        return result


@app.delete("/users/delete")
def delete_user(
    id: int = Query(None),
    name: str = Query(None),
    agency: str = Query(None),
    location: str = Query(None)
):
    if not any([id, name, agency, location]):
        raise HTTPException(
            status_code=400, 
            detail="Provide at least one parameter: id, name, agency, or location"
        )
    
    with Session(engine) as session:
        statement = select(User)
        if id:
            statement = statement.where(User.id == id)
        if name:
            statement = statement.where(User.name == name)
        if agency:
            statement = statement.where(User.agency == agency)
        if location:
            statement = statement.where(User.location == location)
        
        users_to_delete = session.exec(statement).all()
        if not users_to_delete:
            raise HTTPException(status_code=404, detail="No matching users found")
        
        for user in users_to_delete:
            session.delete(user)
        session.commit()
        
        return {"message": f"Deleted {len(users_to_delete)} user(s) successfully"}