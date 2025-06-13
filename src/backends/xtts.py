"""XTTS Backend - High quality GPU-accelerated TTS"""

import logging
import asyncio
import io
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import List, Optional, AsyncGenerator
from ..models import VoiceInfo
from ..config import settings
from . import BaseTTSBackend

logger = logging.getLogger(__name__)


class XTTSBackend(BaseTTSBackend):
    """XTTS backend for high-quality GPU-accelerated TTS"""

    def __init__(self):
        super().__init__()
        self.model = None
        self.device = (
            settings.performance.gpu.device
            if settings.performance.gpu.enabled
            else "cpu"
        )
        self.model_path = Path("./models/xtts")
        self.voices_cache = None
        self.default_voice = "speaker_00"

    async def initialize(self):
        """Initialize XTTS backend"""
        logger.info("Initializing XTTS backend...")

        # Check GPU availability
        if not torch.cuda.is_available() and self.device.startswith("cuda"):
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"

        try:
            # Import TTS library
            from TTS.api import TTS

            # Initialize XTTS model
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

            logger.info(f"Loading XTTS model on {self.device}...")
            self.model = TTS(model_name).to(self.device)

            # Set GPU memory fraction if using CUDA
            if (
                self.device.startswith("cuda")
                and settings.performance.gpu.memory_fraction < 1.0
            ):
                torch.cuda.set_per_process_memory_fraction(
                    settings.performance.gpu.memory_fraction
                )

            logger.info("XTTS backend initialized successfully")

        except Exception as e:
            logger.error(f"XTTS initialization failed: {e}")
            raise

    async def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using XTTS"""
        if not text.strip():
            return b""

        if self.model is None:
            raise Exception("XTTS model not initialized")

        try:
            # Get speaker voice file
            speaker_wav = await self._get_speaker_wav(voice)

            # Generate audio
            loop = asyncio.get_event_loop()
            audio = await loop.run_in_executor(
                None, self._generate_audio_sync, text, speaker_wav
            )

            # Convert to bytes
            audio_bytes = self._audio_to_bytes(audio)
            return audio_bytes

        except Exception as e:
            logger.error(f"XTTS generation failed: {e}")
            raise

    def _generate_audio_sync(self, text: str, speaker_wav: str) -> np.ndarray:
        """Synchronous audio generation for executor"""
        # Use XTTS to generate audio
        audio = self.model.tts(
            text=text, speaker_wav=speaker_wav, language="zh"  # Chinese
        )
        return np.array(audio)

    async def stream_speech(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream speech generation with XTTS"""
        # XTTS doesn't support native streaming, so we'll chunk the text
        sentences = self._split_text(text)

        for sentence in sentences:
            if sentence.strip():
                audio_data = await self.generate_speech(sentence, voice)
                # Stream in chunks
                chunk_size = 4096
                for i in range(0, len(audio_data), chunk_size):
                    yield audio_data[i : i + chunk_size]

    async def get_voices(self) -> List[VoiceInfo]:
        """Get available XTTS voices (speaker embeddings)"""
        if self.voices_cache is None:
            self.voices_cache = []

            # Look for speaker wav files
            speakers_dir = self.model_path / "speakers"
            if speakers_dir.exists():
                for wav_file in speakers_dir.glob("*.wav"):
                    voice_id = wav_file.stem
                    self.voices_cache.append(
                        VoiceInfo(
                            id=voice_id,
                            name=voice_id.replace("_", " ").title(),
                            language="multilingual",
                            gender="unknown",
                            backend="xtts",
                            quality="high",
                        )
                    )

            # Add default speakers
            if not self.voices_cache:
                default_speakers = ["speaker_00", "speaker_01", "speaker_02"]
                for speaker in default_speakers:
                    self.voices_cache.append(
                        VoiceInfo(
                            id=speaker,
                            name=speaker.replace("_", " ").title(),
                            language="multilingual",
                            gender="unknown",
                            backend="xtts",
                            quality="high",
                        )
                    )

            logger.info(f"Found {len(self.voices_cache)} XTTS voices")

        return self.voices_cache

    async def is_available(self) -> bool:
        """Check if XTTS is available"""
        try:
            return self.model is not None and torch.cuda.is_available()
        except Exception:
            return False

    async def _get_speaker_wav(self, voice: Optional[str] = None) -> str:
        """Get speaker WAV file path"""
        speaker_name = voice or self.default_voice

        # Check for custom speaker file
        speakers_dir = self.model_path / "speakers"
        speaker_file = speakers_dir / f"{speaker_name}.wav"

        if speaker_file.exists():
            return str(speaker_file)

        # Use default speaker (you would need to provide sample audio files)
        # For now, we'll use a placeholder
        default_speaker = speakers_dir / "default.wav"
        if default_speaker.exists():
            return str(default_speaker)

        # Create a simple default if none exists
        await self._create_default_speaker(default_speaker)
        return str(default_speaker)

    async def _create_default_speaker(self, output_path: Path):
        """Create a default speaker file (placeholder)"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a simple sine wave as placeholder
        sample_rate = 22050
        duration = 1.0  # 1 second
        frequency = 440  # A4 note

        t = torch.linspace(0, duration, int(sample_rate * duration))
        waveform = torch.sin(2 * torch.pi * frequency * t).unsqueeze(0)

        torchaudio.save(str(output_path), waveform, sample_rate)
        logger.info(f"Created default speaker file: {output_path}")

    def _audio_to_bytes(self, audio: np.ndarray) -> bytes:
        """Convert audio array to WAV bytes"""
        # Normalize audio
        if audio.max() > 1.0 or audio.min() < -1.0:
            audio = audio / np.max(np.abs(audio))

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        # Create WAV file in memory
        buffer = io.BytesIO()

        # Simple WAV header (44 bytes)
        sample_rate = settings.audio.sample_rate
        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = len(audio_int16) * 2
        file_size = 36 + data_size

        # WAV header
        buffer.write(b"RIFF")
        buffer.write(file_size.to_bytes(4, "little"))
        buffer.write(b"WAVE")
        buffer.write(b"fmt ")
        buffer.write((16).to_bytes(4, "little"))  # PCM format
        buffer.write((1).to_bytes(2, "little"))  # Audio format
        buffer.write(num_channels.to_bytes(2, "little"))
        buffer.write(sample_rate.to_bytes(4, "little"))
        buffer.write(byte_rate.to_bytes(4, "little"))
        buffer.write(block_align.to_bytes(2, "little"))
        buffer.write(bits_per_sample.to_bytes(2, "little"))
        buffer.write(b"data")
        buffer.write(data_size.to_bytes(4, "little"))

        # Audio data
        buffer.write(audio_int16.tobytes())

        return buffer.getvalue()

    def _split_text(self, text: str, max_length: int = 200) -> List[str]:
        """Split text into sentences for streaming"""
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in "。！？.!?" and len(current) > 10:
                sentences.append(current.strip())
                current = ""
            elif len(current) >= max_length:
                sentences.append(current.strip())
                current = ""

        if current.strip():
            sentences.append(current.strip())

        return sentences

    async def cleanup(self):
        """Clean up XTTS resources"""
        if self.model is not None:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        logger.info("XTTS backend cleaned up")
