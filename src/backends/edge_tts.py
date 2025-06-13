"""Edge TTS Backend - Fast and free Microsoft TTS"""

import logging
import asyncio
import io
from typing import List, Optional, AsyncGenerator
import edge_tts
from ..models import VoiceInfo
from . import BaseTTSBackend

logger = logging.getLogger(__name__)


class EdgeTTSBackend(BaseTTSBackend):
    """Microsoft Edge TTS backend"""

    def __init__(self):
        super().__init__()
        self.voices_cache = None
        self.default_voice = "zh-CN-XiaoxiaoNeural"

    async def initialize(self):
        """Initialize Edge TTS backend"""
        logger.info("Initializing Edge TTS backend...")

        # Test if Edge TTS is working
        try:
            test_audio = await self.generate_speech("测试", self.default_voice)
            if len(test_audio) > 0:
                logger.info("Edge TTS backend initialized successfully")
            else:
                raise Exception("Edge TTS test failed")
        except Exception as e:
            logger.error(f"Edge TTS initialization failed: {e}")
            raise

    async def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using Edge TTS"""
        if not text.strip():
            return b""

        selected_voice = voice or self.default_voice

        try:
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, selected_voice)

            # Generate audio
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data

        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e}")
            raise

    async def stream_speech(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream speech generation"""
        if not text.strip():
            return

        selected_voice = voice or self.default_voice

        try:
            communicate = edge_tts.Communicate(text, selected_voice)

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        except Exception as e:
            logger.error(f"Edge TTS streaming failed: {e}")
            raise

    async def get_voices(self) -> List[VoiceInfo]:
        """Get available Edge TTS voices"""
        if self.voices_cache is None:
            try:
                voices = await edge_tts.list_voices()
                self.voices_cache = []

                for voice in voices:
                    self.voices_cache.append(
                        VoiceInfo(
                            id=voice["ShortName"],
                            name=voice["FriendlyName"],
                            language=voice["Locale"],
                            gender=voice["Gender"],
                            backend="edge",
                            quality="medium",
                        )
                    )

                logger.info(f"Loaded {len(self.voices_cache)} Edge TTS voices")

            except Exception as e:
                logger.error(f"Failed to load Edge TTS voices: {e}")
                return []

        return self.voices_cache

    async def is_available(self) -> bool:
        """Check if Edge TTS is available"""
        try:
            # Try a quick test
            voices = await edge_tts.list_voices()
            return len(voices) > 0
        except Exception:
            return False
