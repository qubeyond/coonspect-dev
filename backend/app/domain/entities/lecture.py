from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(kw_only=True)
class Lecture:
    id: str | None = None
    author_id: str | None = None

    title: str
    content: dict[str, Any]
    tags: list[str] = field(default_factory=list)

    status: str = "pending"

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update(
        self,
        *,
        title: str | None = None,
        content: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Универсальный метод обновления."""

        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if tags is not None:
            self.tags = tags

        self.updated_at = datetime.now()
