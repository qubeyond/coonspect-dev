from abc import ABC, abstractmethod

from app.domain.entities.lecture import Lecture
from app.domain.entities.value_objects import AuthorId, LectureId


class ILectureRepository(ABC):
    @abstractmethod
    async def add(self, lecture: Lecture) -> LectureId: ...

    @abstractmethod
    async def save(self, lecture: Lecture) -> None: ...

    @abstractmethod
    async def delete(self, lecture_id: LectureId) -> bool: ...

    @abstractmethod
    async def find_by_id(self, lecture_id: LectureId) -> Lecture | None: ...

    @abstractmethod
    async def find_all(
        self, *, limit: int = 10, offset: int = 0, author_id: AuthorId | None = None
    ) -> list[Lecture]: ...

    @abstractmethod
    async def count(self, author_id: AuthorId | None = None) -> int:
        """
        Возвращает общее количество лекций для пагинации.
        """
        ...
