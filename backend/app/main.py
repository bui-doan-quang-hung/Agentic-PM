import os
from datetime import datetime
from enum import Enum
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Status(str, Enum):
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"


class Base(DeclarativeBase):
    pass


class StickyNote(Base):
    __tablename__ = "sticky_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[Priority] = mapped_column(SAEnum(Priority, name="note_priority"), nullable=False)
    status: Mapped[Status] = mapped_column(SAEnum(Status, name="note_status"), nullable=False, default=Status.TODO)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


database_url = os.environ["DATABASE_URL"]
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)

app = FastAPI(title="Sticky Notes API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


class NoteCreate(BaseModel):
    title: str = Field(max_length=255)
    content: str | None = None
    priority: Priority
    status: Status = Status.TODO

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        return value

    @field_validator("status")
    @classmethod
    def new_notes_start_todo(cls, value: Status) -> Status:
        if value != Status.TODO:
            raise ValueError("new notes must start with TODO status")
        return value


class NoteUpdate(BaseModel):
    title: str = Field(max_length=255)
    content: str | None = None
    priority: Priority

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        return value


class StatusUpdate(BaseModel):
    status: Status


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str | None
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(select(1))
    return {"status": "ok"}


@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> StickyNote:
    note = StickyNote(**payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/api/notes", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db)) -> list[StickyNote]:
    return list(db.scalars(select(StickyNote).order_by(StickyNote.id)).all())


def find_note(note_id: int, db: Session) -> StickyNote:
    note = db.get(StickyNote, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.get("/api/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)) -> StickyNote:
    return find_note(note_id, db)


@app.put("/api/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> StickyNote:
    note = find_note(note_id, db)
    for field, value in payload.model_dump().items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@app.patch("/api/notes/{note_id}/status", response_model=NoteOut)
def update_status(note_id: int, payload: StatusUpdate, db: Session = Depends(get_db)) -> StickyNote:
    note = find_note(note_id, db)
    note.status = payload.status
    db.commit()
    db.refresh(note)
    return note


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = find_note(note_id, db)
    db.delete(note)
    db.commit()
    return Response(status_code=204)
