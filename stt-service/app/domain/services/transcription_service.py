from pathlib import Path

from app.domain.entities import TranscriptionTask
from app.domain.interfaces import IAudioProcessor, INotifier, IStorage, ISTTEngine
from app.domain.value_objects import (
    AudioSegment,
    TranscriptionResult,
    TranscriptionStatus,
)


class TranscriptionService:
    def __init__(
        self,
        storage: IStorage,
        audio_processor: IAudioProcessor,
        stt_engine: ISTTEngine,
        notifier: INotifier,
    ):
        self.storage = storage
        self.audio_processor = audio_processor
        self.stt_engine = stt_engine
        self.notifier = notifier

    async def execute(self, task: TranscriptionTask) -> None:
        """
        V1:
        1. Download
        4. Convert
        3. Transcribe
        4. Notify
        """

        local_path: Path | None = None
        processed_path: Path | None = None

        try:
            # Notify Start
            task.update_status(TranscriptionStatus.PROCESSING)
            await self.notifier.notify_status(task)

            # Download
            local_path = await self.storage.download(task.s3_key)

            # Prepare Audio
            processed_path = await self.audio_processor.convert_to_stt(local_path)
            duration = await self.audio_processor.get_duration(processed_path)

            # Transcribe
            input_segment = AudioSegment(
                local_path=processed_path, start_offset=0.0, end_offset=duration
            )
            segments = await self.stt_engine.transcribe(input_segment)

            # Complete & Notify Result
            result = TranscriptionResult(
                full_text=" ".join([s.text for s in segments]).strip(),
                model_name=self.stt_engine.model_name,
                duration_sec=duration,
                segments=segments,
            )
            task.set_result(result)
            await self.notifier.notify_status(task)

        except Exception as e:
            # Handle Failure
            task.set_failed(str(e))
            await self.notifier.notify_status(task)

        finally:
            # Cleanup
            if local_path:
                await self.storage.delete_local(local_path)
            if processed_path and processed_path != local_path:
                await self.storage.delete_local(processed_path)
