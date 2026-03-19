import string

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
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

def from_base62(s):

    chars = string.digits + string.ascii_letters

    char_map = {char: i for i, char in enumerate(chars)}

    num = 0
    for char in s:

        num = num * 62 + char_map[char]
    return num

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


@app.get("/{short_code}")

async def redirect_url(short_code: str, db: Session = Depends(get_session)):

    url_id = from_base62(short_code)

    db_url = db.exec(select(URL).where(URL.id == url_id)).first()

    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=db_url.long_url, status_code=302)