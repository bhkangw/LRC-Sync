from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from process import process_audio

app = FastAPI(title="LRC Sync API")

class ProcessRequest(BaseModel):
    audio_url: HttpUrl
    lyrics: str

@app.post("/process")
async def process(request: ProcessRequest):
    """Process audio URL and lyrics to generate synchronized LRC"""
    try:
        result = process_audio(str(request.audio_url), request.lyrics)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 