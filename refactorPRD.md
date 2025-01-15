# Product Requirements Document (PRD): Refactoring SRT-Sync to Integrate with suno-to-csv

## 1. Objective

The goal is to refactor the existing SRT-Sync repository to:

1. Accept audio URLs and raw lyrics text as inputs
2. Automate the two-step process (Transcription → Synchronization)
3. Expose the process via an API to integrate with the suno-to-csv workflow
4. Generate and return synchronized LRC content as raw text, suitable for storage in the CSV

## 2. Problem Statement

Currently, the SRT-Sync workflow:

- Requires local MP3 files for transcription
- Relies on manual commands to trigger transcription and synchronization steps
- Outputs SRT files but doesn't directly support LRC file generation
- Has no API integration for seamless automation

These limitations make it inefficient for large-scale workflows like suno-to-csv, which processes metadata for hundreds of songs at a time.

## 3. Scope

The refactor will:

### 3.1 Enable remote processing

- Accept audio URLs instead of local MP3 files
- Accept raw lyrics as text or from a file

### 3.2 Automate the workflow

- Automatically link transcription and synchronization steps
- Eliminate manual command execution

### 3.3 Generate and output LRC content

- Convert synchronized SRT files into LRC format
- Return raw LRC text for integration with the suno-to-csv workflow

### 3.4 Integrate via API

- Expose the workflow as an API using FastAPI
- Allow suno-to-csv to send inputs (audio URLs and lyrics) and receive outputs (LRC text)

### 3.5 Optimize for large datasets

- Process up to 200 songs per batch efficiently
- Leverage Google Colab or GPU-accelerated environments for transcription

## 4. Functional Requirements

### Inputs

- Audio URL: A publicly accessible URL pointing to an MP3 file
- Lyrics Text: Raw lyrics, preserving line breaks (input as text or read from a file)

### Outputs

- LRC Text: Raw synchronized lyrics in LRC format, returned as a JSON response (stringified so as to be stored in the CSV, then uploaded to supabase as a JSONB column)

### API Endpoint

- Endpoint: `/process`
- Method: POST
- Request Body:

```json
{
  "audio_url": "https://example.com/song.mp3",
  "lyrics": "Do you ever feel\nLike a plastic bag..."
}
```

- Response:

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

## 5. Non-Functional Requirements

### 5.1 Performance

- Transcription must process a single song in under 2 minutes using GPU acceleration
- Batch processing of 200 songs should scale efficiently

### 5.2 Scalability

- The system must support parallel API requests for multiple songs

### 5.3 Error Handling

- Handle invalid audio URLs gracefully (e.g., return meaningful error messages)
- Validate and sanitize input lyrics

### 5.4 Ease of Deployment

- Must be deployable on Google Colab for GPU usage
- Should also run locally for debugging

## 6. High-Level Architecture

### Workflow

1. **Transcription**

   - Input: Audio URL
   - Action: Download MP3, transcribe, and save as a temporary SRT file (transcribe.py)
   - Output: Initial SRT file

2. **Synchronization**

   - Input: SRT file and raw lyrics
   - Action: Align transcription with raw lyrics, generating a synchronized SRT file (srtSync.py)
   - Output: Synchronized SRT file

3. **LRC Conversion**

   - Input: Synchronized SRT file
   - Action: Convert SRT timestamps and text into LRC format
   - Output: LRC json stringified so as to be stored in the CSV, then uploaded to supabase as a JSONB column

4. **API Integration**
   - Input: Audio URL and lyrics
   - Action: Call transcription, synchronization, and LRC conversion
   - Output: Return LRC json stringified so as to be stored in the CSV, then uploaded to supabase as a JSONB column

## 7. Technical Design

### Key Changes

1. **Refactor Transcription (Transcribe.py)**

   - Accept an audio URL
   - Download the MP3 file temporarily
   - Transcribe

2. **Refactor Synchronization (SrtSync.py)**

   - Expose synchronization as a function
   - Accept raw lyrics as a string

3. **Create Unified Workflow (Process.py)**

   - Chain transcription, synchronization, and LRC conversion
   - Automate the full pipeline

4. **Build API (App.py)**

   - Use FastAPI to expose the workflow as a POST endpoint

5. **Optimize Environment**
   - Set up Colab for GPU acceleration
   - Cache Whisper models in Google Drive to avoid re-downloading

## 8. Example Workflow

1. **API Request**

   ```json
   {
     "audio_url": "https://example.com/song.mp3",
     "lyrics": "Do you ever feel\nLike a plastic bag..."
   }
   ```

2. **Transcription**

   - Download the MP3
   - Transcribe and save temp_output.srt

3. **Synchronization**

   - Align temp_output.srt with lyrics
   - Save temp_synced.srt

4. **LRC Conversion**

   ```
   [00:01.00]Do you ever feel
   [00:05.20]Like a plastic bag
   ...
   ```

5. **API Response**
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

## 9. Deployment Plan

### Local Testing

- Run the workflow locally using sample inputs
- Test both command-line execution and API calls

### Google Colab Deployment

- Run the refactored code in Colab with GPU
- Cache Whisper models in Google Drive to reduce startup times

### Integration with suno-to-csv

- Call the /process API for each song in the playlist
- Store the returned lrc in the CSV's lrc_text column

## 10. Future Enhancements

- Batch Processing: Accept multiple songs in one API request
- Real-Time Progress Updates: Add WebSocket support for long-running jobs
- Enhanced Outputs: Support SRT, LRC, and JSON formats for maximum flexibility
