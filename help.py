import os
import secrets
import asyncio
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse
from pyrogram import Client
from pyrogram.types import Message
import random

API_ID = 21613005
API_HASH = "083d8033c044608267978d2f04d8b0d5"
SESSION_PATH = "/home/ubuntu/hello/anon"
CHANNEL = "https://t.me/AnimeHentai_Sex"
VPS_IP = "129.146.180.197"
DOWNLOAD_DIR = "/home/ubuntu/hello/videos"

app = FastAPI()
client = Client(SESSION_PATH, api_id=API_ID, api_hash=API_HASH)
active_tokens = {}

@app.on_event("startup")
async def startup_event():
    await client.start()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    await client.stop()

@app.get("/get_video")
async def get_video():
    async for message in client.get_chat_history(CHANNEL, limit=50):
        if isinstance(message, Message) and message.video:
            if 600 <= message.video.duration <= 1500:
                file_path = os.path.join(DOWNLOAD_DIR, f"{message.video.file_unique_id}.mp4")
                if not os.path.exists(file_path):
                    await message.download(file_name=file_path)
                token = secrets.token_urlsafe(16)
                active_tokens[token] = file_path
                return {"status": "success", "url": f"http://{VPS_IP}:9000/download/{token}"}
    raise HTTPException(status_code=404, detail="No suitable video found")

@app.get("/download/{token}")
async def download_file(token: str):
    file_path = active_tokens.pop(token, None)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    async def delete_file_after_response():
        await asyncio.sleep(1)
        os.remove(file_path)
    asyncio.create_task(delete_file_after_response())
    return FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))
