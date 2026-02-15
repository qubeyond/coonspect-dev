from abc import ABC, abstractmethod

from app.domain.entities.lecture import Lecture


class ILectureRepository(ABC):
    @abstractmethod
    async def create(self, lecture: Lecture) -> str:
        ...

    @abstractmethod
    async def get_by_id(self, lecture_id: str) -> Lecture | None:
        ...

    @abstractmethod
    async def update(self, lecture: Lecture) -> None:
        ...

    @abstractmethod
    async def delete(self, lecture_id: str) -> bool:
        ...

    @abstractmethod
    async def find_many(
        self, 
        *, 
        limit: int = 10, 
        offset: int = 0,
        author_id: str | None = None
    ) -> list[Lecture]:
        """
        Массовое получение лекций. 
        Позволяет фильтровать по автору и использовать пагинацию.
        """
        ...

    @abstractmethod
    async def count(self, author_id: str | None = None) -> int:
        """Возвращает общее количество лекций."""
        ...