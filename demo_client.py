"""Demo client for testing TTS server"""

import asyncio
import websockets
import json
import base64
import wave
from pathlib import Path
import httpx


class TTSClient:
    """Demo client for TTS server"""

    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws") + "/ws"

    async def test_rest_api(self, text="你好，这是一个测试。"):
        """Test REST API"""
        print(f"Testing REST API with text: {text}")

        async with httpx.AsyncClient() as client:
            # Test TTS generation
            response = await client.post(
                f"{self.server_url}/tts",
                json={"text": text, "voice": "zh-CN-XiaoxiaoNeural", "backend": "edge"},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ TTS generated successfully")
                print(f"  Backend: {data['metadata']['backend']}")
                print(f"  Cached: {data['cached']}")

                # Save audio file
                audio_data = base64.b64decode(data["audio_data"])
                output_file = Path("test_output.wav")
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"  Audio saved to: {output_file}")

            else:
                print(f"✗ TTS failed: {response.status_code} - {response.text}")

    async def test_websocket(self, text="WebSocket测试文本"):
        """Test WebSocket streaming"""
        print(f"Testing WebSocket with text: {text}")

        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Send TTS request
                await websocket.send(
                    json.dumps(
                        {"type": "tts", "text": text, "voice": "zh-CN-XiaoxiaoNeural"}
                    )
                )

                # Receive audio chunks
                audio_chunks = []
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)

                        if isinstance(message, bytes):
                            # Audio chunk
                            audio_chunks.append(message)
                        else:
                            # JSON message
                            data = json.loads(message)
                            if data.get("type") == "complete":
                                print("✓ WebSocket streaming completed")
                                break
                            elif data.get("type") == "error":
                                print(f"✗ WebSocket error: {data['message']}")
                                return

                    except asyncio.TimeoutError:
                        print("✗ WebSocket timeout")
                        break

                # Save streamed audio
                if audio_chunks:
                    output_file = Path("test_stream.wav")
                    with open(output_file, "wb") as f:
                        for chunk in audio_chunks:
                            f.write(chunk)
                    print(f"  Streamed audio saved to: {output_file}")

        except Exception as e:
            print(f"✗ WebSocket connection failed: {e}")

    async def test_voices(self):
        """Test voice listing"""
        print("Testing voice listing...")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.server_url}/voices")

            if response.status_code == 200:
                voices = response.json()
                print(f"✓ Found {len(voices)} voices")

                # Show first few voices
                for voice in voices[:5]:
                    print(
                        f"  {voice['id']} - {voice['name']} ({voice['language']}) [{voice['backend']}]"
                    )

                if len(voices) > 5:
                    print(f"  ... and {len(voices) - 5} more")
            else:
                print(f"✗ Failed to get voices: {response.status_code}")

    async def test_backends(self):
        """Test backend status"""
        print("Testing backend status...")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.server_url}/backends")

            if response.status_code == 200:
                backends = response.json()
                print("✓ Backend status:")
                for backend in backends:
                    status = "🟢" if backend["available"] else "🔴"
                    print(f"  {status} {backend['name']} - Load: {backend['load']:.1%}")
            else:
                print(f"✗ Failed to get backend status: {response.status_code}")

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting TTS Server Tests\n")

        # Test server health
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/")
                if response.status_code == 200:
                    print("✓ Server is running\n")
                else:
                    print("✗ Server not responding")
                    return
        except Exception as e:
            print(f"✗ Cannot connect to server: {e}")
            return

        # Run tests
        await self.test_backends()
        print()

        await self.test_voices()
        print()

        await self.test_rest_api()
        print()

        await self.test_websocket()
        print()

        print("🎉 All tests completed!")


async def main():
    """Main function"""
    client = TTSClient()
    await client.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
