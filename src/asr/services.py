import os
from typing import Iterable, Optional

from src.core.settings import app_settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class WhisperTurboService:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        if OpenAI is None:
            raise RuntimeError("openai package is not installed")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = getattr(app_settings, "openai_asr_model", "whisper-1")

    def transcribe(self, file_path: str, **kwargs) -> dict:
        with open(file_path, "rb") as f:
            resp = self.client.audio.transcriptions.create(
                model=self.model,
                file=f,
                **kwargs,
            )
        # OpenAI SDK returns an object with .text and possibly .segments
        result = {
            "text": getattr(resp, "text", ""),
        }
        segments = getattr(resp, "segments", None)
        if segments:
            result["segments"] = [
                {
                    "start": getattr(seg, "start", None),
                    "end": getattr(seg, "end", None),
                    "text": getattr(seg, "text", None),
                }
                for seg in segments
            ]
        return result
