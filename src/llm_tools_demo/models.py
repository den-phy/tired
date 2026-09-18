from sqlalchemy import Boolean, Identity, String, false
from sqlalchemy.orm import Mapped, mapped_column

from llm_tools_demo.database import Base


class TodoModel(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )
