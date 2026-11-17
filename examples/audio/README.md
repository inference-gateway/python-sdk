# Audio API Example

This example demonstrates speech, sound-effect and music generation via the Audio API using the Inference Gateway Python SDK. It shows how to:

- Synthesize speech from text with `create_speech` (`POST /audio/speech`)
- Generate a sound effect from a text prompt with `create_sfx` (`POST /audio/sfx`)
- Score a video with `create_sfx` (optional)
- Compose an instrumental music clip with `create_music` (`POST /audio/music`)

All three methods return the generated audio as raw `bytes`, not a response model. Write them to a file or stream them to a player.

**Prerequisites:**

- The Inference Gateway must run with `AUDIO_ENABLED=true`.
- A provider with audio support must be configured with its API key in the `.env` file - for example `openai` (speech), `elevenlabs` (speech, sound effects, music) or `mirelo` (sound effects and video scoring).
- Requests routed to a provider without support for an endpoint return a 400 error, raised as `InferenceGatewayAPIError`. The same happens when a provider cannot honor a given field.

## Usage

1. **Set up environment**:

   ```bash
   export SPEECH_MODEL="openai/gpt-4o-mini-tts"
   export SFX_MODEL="elevenlabs/eleven_text_to_sound_v2"
   export MUSIC_MODEL="elevenlabs/music_v2_5"
   ```

2. **Run the example**:

   ```bash
   python main.py
   ```

   The audio is written to `speech.mp3`, `sfx.mp3` and `music.mp3` in the current directory.

3. **Optional - demo video scoring**: set a video URL (an https URL or a base64 `data:video/...` URI):

   ```bash
   export VIDEO_URL=https://example.com/clip.mp4
   export VIDEO_SFX_MODEL="mirelo/sfx-2.0"
   ```

## Code Examples

### Speech

```python
from inference_gateway import InferenceGatewayClient

client = InferenceGatewayClient("http://localhost:8080/v1")

audio = client.create_speech(
    model="openai/gpt-4o-mini-tts",
    input="Hello from the Inference Gateway Python SDK!",
    voice="alloy",
)

with open("speech.mp3", "wb") as f:
    f.write(audio)
```

### Sound Effect from Text

```python
audio = client.create_sfx(
    model="elevenlabs/eleven_text_to_sound_v2",
    prompt="Thunder rumbling over a quiet forest",
    duration_seconds=5,
)
```

Text-only arguments: `prompt` (required without `video`), `prompt_influence` and `loop`.

### Sound Effect for a Video

```python
audio = client.create_sfx(
    model="mirelo/sfx-2.0",
    video="https://example.com/clip.mp4",
    output="sfx",
)
```

Video-only arguments: `start_offset_seconds`, `preserve_speech` and `output` (`mix`, `sfx` or `speech`). With a video the `prompt` is optional guidance. `duration_seconds` sets the clip length for text and the scored window for a video.

### Music

```python
audio = client.create_music(
    model="elevenlabs/music_v2_5",
    prompt="Upbeat lo-fi hip hop with mellow piano",
    duration_seconds=15,
    instrumental=True,
)
```

### Audio Format

Every method accepts `response_format` to pick the audio encoding. The default is `mp3`. `create_speech` supports `mp3`, `opus`, `aac`, `flac`, `wav` and `pcm`. `create_sfx` and `create_music` support `mp3`, `opus`, `aac`, `flac` and `pcm`.

```python
audio = client.create_speech(
    model="openai/gpt-4o-mini-tts",
    input="Hello!",
    voice="nova",
    response_format="wav",
)
```

## Configuration

The example uses these environment variables:

- `SPEECH_MODEL`: Model for `create_speech` (default: `openai/gpt-4o-mini-tts`)
- `SFX_MODEL`: Model for text-to-sfx (default: `elevenlabs/eleven_text_to_sound_v2`)
- `MUSIC_MODEL`: Model for `create_music` (default: `elevenlabs/music_v2_5`)
- `VIDEO_URL`: Optional video to score with `create_sfx`
- `VIDEO_SFX_MODEL`: Model for video scoring (default: `mirelo/sfx-2.0`)
