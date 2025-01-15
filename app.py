from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from process import process_audio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="LRC Sync API")

class ProcessRequest(BaseModel):
    audio_url: HttpUrl
    lyrics: str

@app.post("/process")
async def process(request: ProcessRequest):
    """Process audio URL and lyrics to generate synchronized LRC"""
    try:
        logger.info(f"Processing request for audio URL: {request.audio_url}")
        result = process_audio(str(request.audio_url), request.lyrics)
        logger.info("Successfully processed audio")
        return result
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "An error occurred while processing the audio file. Check the logs for more details."
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 