from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class TranscriptionStatus(StrEnum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AudioSegment:
    local_path: Path
    start_offset: float
    end_offset: float


@dataclass(frozen=True)
class TranscriptionSegment:
    text: str
    start_offset: float
    end_offset: float
    confidence: float | None = None


@dataclass(frozen=True)
class TranscriptionResult:
    full_text: str
    model_name: str  # хз, наверное лишнее, для отчетов
    duration_sec: float
    segments: list[TranscriptionSegment]
