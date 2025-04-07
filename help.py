import os
import random
import secrets
import asyncio
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse
from pyrogram import Client
from pyrogram.types import Message

api_id = 21613005
api_hash = "083d8033c044608267978d2f04d8b0d5"
VPS_IP = "129.146.180.197"
VIDEO_DIR = "downloads"
TOKEN_MAP = {}
CHANNEL = "AnimeHentai_Sex"

app = FastAPI()
client = Client("anon", api_id=api_id, api_hash=api_hash)

@app.on_event("startup")
async def startup_event():
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    await client.start()

@app.on_event("shutdown")
async def shutdown_event():
    await client.stop()

@app.get("/get_video")
async def get_video():
    messages = []
    async for msg in client.get_chat_history(CHANNEL, limit=100):
        if msg.video and 600 <= msg.video.duration <= 1500:
            messages.append(msg)

    if not messages:
        raise HTTPException(status_code=404, detail="No suitable video found")

    selected: Message = random.choice(messages)
    file_path = await client.download_media(selected, file_name=VIDEO_DIR)

    if not file_path:
        raise HTTPException(status_code=500, detail="Download failed")

    token = secrets.token_urlsafe(16)
    TOKEN_MAP[token] = file_path

    return {"status": "success", "download_url": f"http://{VPS_IP}:69/download/{token}"}

@app.get("/download/{token}")
async def download_file(token: str):
    if token not in TOKEN_MAP:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    file_path = TOKEN_MAP.pop(token)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    async def delete_after_send():
        await asyncio.sleep(5)
        if os.path.exists(file_path):
            os.remove(file_path)

    asyncio.create_task(delete_after_send())

    return FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))
