import os

from inference_gateway import InferenceGatewayClient
from inference_gateway.client import InferenceGatewayAPIError, InferenceGatewayError


def save(path: str, audio: bytes) -> None:
    """Write raw audio bytes returned by the Audio API to a file."""
    with open(path, "wb") as f:
        f.write(audio)
    print(f"Saved {len(audio)} bytes to {path}")


def main() -> None:
    """
    Demo of speech, sound-effect and music generation via the
    Audio API using the Inference Gateway Python SDK.
    """
    client = InferenceGatewayClient("http://localhost:8080/v1")

    speech_model = os.getenv("SPEECH_MODEL", "openai/gpt-4o-mini-tts")
    sfx_model = os.getenv("SFX_MODEL", "elevenlabs/eleven_text_to_sound_v2")
    music_model = os.getenv("MUSIC_MODEL", "elevenlabs/music_v2_5")
    video_url = os.getenv("VIDEO_URL")

    try:
        print(f"Speech with {speech_model}")
        speech = client.create_speech(
            model=speech_model,
            input="Hello from the Inference Gateway Python SDK!",
            voice="alloy",
        )
        save("speech.mp3", speech)

        print(f"Sound effect with {sfx_model}")
        sfx = client.create_sfx(
            model=sfx_model,
            prompt="Thunder rumbling over a quiet forest",
            duration_seconds=5,
        )
        save("sfx.mp3", sfx)

        if video_url:
            video_sfx_model = os.getenv("VIDEO_SFX_MODEL", "mirelo/sfx-2.0")
            print(f"Scoring video with {video_sfx_model}")
            scored = client.create_sfx(model=video_sfx_model, video=video_url, output="sfx")
            save("video_sfx.mp3", scored)
        else:
            print("Set VIDEO_URL=https://... to demo video scoring")

        print(f"Music with {music_model}")
        music = client.create_music(
            model=music_model,
            prompt="Upbeat lo-fi hip hop with mellow piano",
            duration_seconds=15,
            instrumental=True,
        )
        save("music.mp3", music)

    except (InferenceGatewayAPIError, InferenceGatewayError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
