"""Piper TTS Backend - Fast local neural TTS"""

import logging
import subprocess
import json
import io
from pathlib import Path
from typing import List, Optional, AsyncGenerator
from src.models import VoiceInfo
from . import BaseTTSBackend

logger = logging.getLogger(__name__)


class PiperTTSBackend(BaseTTSBackend):
    """Piper TTS backend for fast local inference"""

    def __init__(self):
        super().__init__()
        self.model_path = Path("./models/piper")
        self.voices_cache = None
        self.default_voice = "zh_CN-huayan-medium"

    async def initialize(self):
        """Initialize Piper TTS backend"""
        logger.info("Initializing Piper TTS backend...")

        # Check if piper is installed
        try:
            result = subprocess.run(["piper", "--help"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Piper TTS found")
            else:
                raise Exception("Piper TTS not found")
        except FileNotFoundError:
            logger.warning("Piper TTS not installed. Run: pip install piper-tts")
            raise Exception("Piper TTS not available")

        # Ensure models directory exists
        self.model_path.mkdir(parents=True, exist_ok=True)

        # Download default model if not exists
        await self._ensure_default_model()

        logger.info("Piper TTS backend initialized successfully")

    async def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using Piper TTS"""
        if not text.strip():
            return b""

        selected_voice = voice or self.default_voice
        model_file = self.model_path / f"{selected_voice}.onnx"

        if not model_file.exists():
            logger.warning(f"Model {selected_voice} not found, using default")
            model_file = self.model_path / f"{self.default_voice}.onnx"

        if not model_file.exists():
            raise Exception(f"No Piper model available")

        try:
            # Run piper TTS
            cmd = [
                "piper",
                "--model",
                str(model_file),
                "--output_file",
                "-",  # Output to stdout
            ]

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate(input=text.encode("utf-8"))

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {stderr.decode()}")
                raise Exception(f"Piper TTS generation failed")

            return stdout

        except Exception as e:
            logger.error(f"Piper TTS generation failed: {e}")
            raise

    async def get_voices(self) -> List[VoiceInfo]:
        """Get available Piper voices"""
        if self.voices_cache is None:
            self.voices_cache = []

            # Scan for .onnx model files
            if self.model_path.exists():
                for model_file in self.model_path.glob("*.onnx"):
                    voice_id = model_file.stem

                    # Try to load voice info from .json file
                    json_file = model_file.with_suffix(".onnx.json")
                    if json_file.exists():
                        try:
                            with open(json_file, "r", encoding="utf-8") as f:
                                voice_info = json.load(f)

                            self.voices_cache.append(
                                VoiceInfo(
                                    id=voice_id,
                                    name=voice_info.get("name", voice_id),
                                    language=voice_info.get("language", {}).get(
                                        "code", "unknown"
                                    ),
                                    gender=voice_info.get("speaker_id_map", {}).get(
                                        "0", "unknown"
                                    ),
                                    backend="piper",
                                    quality="high",
                                )
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to parse voice info for {voice_id}: {e}"
                            )
                    else:
                        # Create basic voice info
                        self.voices_cache.append(
                            VoiceInfo(
                                id=voice_id,
                                name=voice_id,
                                language="unknown",
                                gender="unknown",
                                backend="piper",
                                quality="high",
                            )
                        )

            logger.info(f"Found {len(self.voices_cache)} Piper voices")

        return self.voices_cache

    async def is_available(self) -> bool:
        """Check if Piper TTS is available"""
        try:
            result = subprocess.run(["piper", "--help"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _ensure_default_model(self):
        """Download default model if not available"""
        model_file = self.model_path / f"{self.default_voice}.onnx"

        if not model_file.exists():
            logger.info(f"Downloading default Piper model: {self.default_voice}")
            try:
                # Download model using piper's download functionality
                cmd = [
                    "piper",
                    "--download-dir",
                    str(self.model_path),
                    "--download",
                    self.default_voice,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Default Piper model downloaded successfully")
                else:
                    logger.warning(f"Failed to download default model: {result.stderr}")
            except Exception as e:
                logger.warning(f"Failed to download default Piper model: {e}")
