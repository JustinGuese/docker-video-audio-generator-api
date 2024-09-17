from enum import Enum
from os import environ

from faster_whisper import WhisperModel

MODEL_SIZE = "medium.en"


class WhisperDevice(Enum):
    CPU = "cpu"
    GPU = "gpu"
    MPS = "mps"


def __format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


def createTranscript(
    filename: str,
    device: WhisperDevice = WhisperDevice(environ.get("WHISPER_DEVICE", "cpu")),
) -> str:
    # Run on GPU with FP16
    model = WhisperModel(MODEL_SIZE, device=device.value)
    segments, info = model.transcribe(filename, language="en-US")

    with open(filename.replace(".mp3", ".srt"), "w", encoding="utf-8") as srt_file:
        for segment in segments:
            start_time = __format_time(segment.start)
            end_time = __format_time(segment.end)
            text = segment.text
            segment_id = segment.id + 1
            # line_out = f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
            srt_file.write(
                f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
            )
