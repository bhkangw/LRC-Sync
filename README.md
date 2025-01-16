# SRT-Sync

Synchronize SRT timestamps over an existing accurate transcription, now with API support!

## Features

- Accept audio URLs and raw lyrics as input
- Automated transcription and synchronization pipeline
- FastAPI endpoint for easy integration
- Output in LRC JSON format
- GPU acceleration support via Whisper

## Installation

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# if not already installed
brew install ffmpeg
```

## Usage

### As an API

1. Start the server:

```bash
python app.py
```

2. Make a POST request to `/process`:

```json
{
  "audio_url": "https://example.com/song.mp3",
  "lyrics": "Do you ever feel\nLike a plastic bag..."
}
```

3. Get synchronized lyrics in response:
DESIRED OUTPUT
```json
{
  "lines": [
    {
      "timestamp": 1000,
      "text": "Do you ever feel"
    },
    {
      "timestamp": 5200,
      "text": "Like a plastic bag"
    }
  ]
}
```

## Google Colab

This code is optimized to run on Google Colab for GPU acceleration. Simply:

1. Upload the code to Colab
2. Install dependencies:

```
!pip install -r requirements.txt
!apt-get install ffmpeg
```

3. Run the FastAPI server:

```python
!python app.py
```
