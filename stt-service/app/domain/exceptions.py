class DomainError(Exception):
    message: str


class AudioTooLongError(DomainError):
    def __init__(self, duration: float) -> None:
        self.message = f"Audio is too long: {duration}s. Max allowed is {3600}s."


class StorageFileNotFoundError(DomainError):
    def __init__(self, s3_key: str) -> None:
        self.message = f"File not found in storage: {s3_key}"


class STTProcessingError(DomainError):
    def __init__(self, details: str) -> None:
        self.message = f"GPU processing failed: {details}"
