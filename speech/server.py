import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse  # <-- Added FileResponse
from google import genai
from google.genai import types

app = FastAPI()
client = genai.Client()

SYSTEM_PROMPT = """
You are a real-time translator. You will receive an audio clip of spoken English.
1. Transcribe the spoken English accurately into text.
2. Translate that text into natural Korean.

Output strictly in JSON format matching this schema:
{"english": "Transcribed English text", "korean": "Korean translation"}
"""

# Serve index.html at http://localhost:8000/
@app.get("/")
async def get_index():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            audio_b64 = await websocket.receive_text()
            audio_bytes = base64.b64decode(audio_b64)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    SYSTEM_PROMPT
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            await websocket.send_text(response.text)

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
