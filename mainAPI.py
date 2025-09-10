from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from contextlib import asynccontextmanager
import logging
import os

# ----------------------------
# Configure logging
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------
# Neon Postgres connection string
# ----------------------------
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://neondb_owner:npg_LN0caK9xfCTl@ep-crimson-sky-ad4jbazk-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# ----------------------------
# Create SQLAlchemy engine
# ----------------------------
engine = create_engine(DATABASE_URL, echo=True)

# ----------------------------
# Define SQLModel
# ----------------------------
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    agency: str
    location: str
    genres: str
    website: str

# ----------------------------
# Create tables if they don’t exist
# ----------------------------
def create_db_and_tables():
    logger.info("Creating database tables if they don't exist...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tables created or already exist.")

# ----------------------------
# FastAPI lifespan (runs at startup)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# ----------------------------
# Initialize app
# ----------------------------
app = FastAPI(lifespan=lifespan, title="Item API")

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Item API"}

@app.get("/items_debug")
def read_items_debug():
    """Debug endpoint: Returns items or error message."""
    try:
        with Session(engine) as session:
            items = session.exec(select(Item)).all()
            logger.info(f"Retrieved {len(items)} items from DB.")
            return {"items_count": len(items), "items": items}
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return {"error": str(e)}

@app.get("/items/", response_model=List[Item])
def read_items(limit: int = 100):
    """Return first `limit` items."""
    try:
        with Session(engine) as session:
            items = session.exec(select(Item).limit(limit)).all()
            logger.info(f"Returning {len(items)} items.")
            return items
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items/")
def create_item(item: Item):
    try:
        with Session(engine) as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            logger.info(f"Created item with ID: {item.id}")
            return item
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail=str(e))