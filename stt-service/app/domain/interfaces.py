from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.entities import TranscriptionTask
from app.domain.value_objects import AudioSegment, TranscriptionSegment


class IStorage(ABC):
    @abstractmethod
    async def download(self, s3_key: str) -> Path: ...

    @abstractmethod
    async def delete_local(self, local_path: Path) -> None: ...


class IAudioProcessor(ABC):
    @abstractmethod
    async def get_duration(self, local_path: Path) -> float: ...

    @abstractmethod
    async def convert_to_stt(self, local_path: Path) -> Path: ...


class ISTTEngine(ABC):
    @abstractmethod
    async def transcribe(self, segment: AudioSegment) -> list[TranscriptionSegment]: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...


class INotifier(ABC):
    @abstractmethod
    async def notify_status(self, task: TranscriptionTask) -> None: ...
