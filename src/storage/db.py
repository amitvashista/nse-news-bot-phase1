
from __future__ import annotations

from typing import List, Dict

from sqlalchemy import (
    create_engine,
    String,
    DateTime,
    Text,
    select,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session

Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    published_at: Mapped[str] = mapped_column(String(32), nullable=True)
    company_symbols: Mapped[str] = mapped_column(Text, nullable=True)  # comma-separated for Phase 1
    raw: Mapped[str] = mapped_column(Text, nullable=True)


class NewsDB:
    def __init__(self, path: str):
        self.engine = create_engine(f"sqlite:///{path}", future=True)

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def insert_many(self, items: List[Dict]) -> int:
        if not items:
            return 0
        rows = 0
        with Session(self.engine) as s:
            for it in items:
                # Upsert-lite: skip if URL exists
                exists = s.execute(select(News).where(News.url == it.get("url"))).scalar_one_or_none()
                if exists:
                    continue
                row = News(
                    source=it.get("source", ""),
                    title=it.get("title", ""),
                    summary=it.get("summary"),
                    url=it.get("url", ""),
                    published_at=it.get("published_at"),
                    company_symbols=",".join(it.get("company_symbols") or []),
                    raw=str(it.get("raw")) if it.get("raw") is not None else None,
                )
                s.add(row)
                rows += 1
            s.commit()
        return rows
