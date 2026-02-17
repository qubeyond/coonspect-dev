from dataclasses import dataclass

from app.domain.value_objects import TranscriptionResult, TranscriptionStatus


@dataclass
class TranscriptionTask:
    id: str  # UUID
    file_id: str
    s3_key: str

    status: TranscriptionStatus = TranscriptionStatus.PENDING
    result: TranscriptionResult | None = None
    error_message: str | None = None

    def update_status(self, status: TranscriptionStatus) -> None:
        self.status = status

    def set_result(self, result: TranscriptionResult) -> None:
        self.result = result
        self.status = TranscriptionStatus.COMPLETED

    def set_failed(self, error: str) -> None:
        self.error_message = error
        self.status = TranscriptionStatus.FAILED
