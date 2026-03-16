import string

from fastapi import FastAPI, Depends
from sqlmodel import Field, Session, SQLModel, create_engine
from pydantic import HttpUrl

from typing import Optional

class URL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    long_url: str

class URLRequest(SQLModel):

    long_url: HttpUrl

engine = create_engine("sqlite:///./urls.db", echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def to_base62(num):
    chars = string.digits + string.ascii_letters
    if num == 0:
        return chars[0]
    base62 = []
    while num > 0:
        num, rem = divmod(num, 62)
        base62.append(chars[rem])
    return "".join(reversed(base62))

app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/shorten")

async def shorten_url(url_request: URLRequest, db: Session = Depends(get_session)):

    db_url = URL(long_url=str(url_request.long_url))
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    short_code = to_base62(db_url.id)

    short_url = f"http://127.0.0.1:8000/{short_code}"
    return {"short_url": short_url}