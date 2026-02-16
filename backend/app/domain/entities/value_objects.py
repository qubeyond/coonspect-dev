from dataclasses import dataclass


@dataclass(frozen=True)
class LectureId:
    value: str


@dataclass(frozen=True)
class AuthorId:
    value: str


@dataclass(frozen=True)
class Title:
    value: str

    def __post_init__(self) -> None:
        if not (1 <= len(self.value) <= 255):
            raise ValueError("Title must be between 1 and 255 characters")


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str | None = None
    confidence: float | None = None

    def is_empty(self) -> bool:
        return len(self.text.strip()) == 0


@dataclass(frozen=True)
class Tag:
    value: str

    def __post_init__(self) -> None:
        if not (1 <= len(self.value) <= 20):
            raise ValueError("Tag must be 1-20 chars")
        object.__setattr__(self, "value", self.value.lower().strip())


class DomainError(Exception): ...


class InvalidStateTransitionError(DomainError): ...
