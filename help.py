import os
import random
import secrets
import asyncio
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse
from pyrogram import Client
from pyrogram.errors import FloodWait

api_id = 21613005
api_hash = "083d8033c044608267978d2f04d8b0d5"
channel = "AnimeHentai_Sex"
download_dir = "downloads"
token_map = {}
vps_ip = "129.146.180.197"

app = FastAPI()
client = Client("anon", api_id=api_id, api_hash=api_hash)

@app.on_event("startup")
async def startup_event():
    os.makedirs(download_dir, exist_ok=True)
    await client.start()

@app.get("/get_video")
async def get_random_video():
    async for msg in client.get_chat_history(channel, limit=200):
        try:
            if msg.video and 600 <= msg.video.duration <= 1500:
                file_name = f"{msg.video.file_name or msg.video.file_id}.mp4"
                file_path = os.path.join(download_dir, file_name)

                if not os.path.exists(file_path):
                    await msg.download(file_path)

                token = secrets.token_urlsafe(12)
                token_map[token] = file_path

                return {
                    "download": f"http://{vps_ip}:69/download/{token}",
                    "filename": file_name,
                    "duration": msg.video.duration
                }
        except FloodWait as e:
            await asyncio.sleep(e.value)

    raise HTTPException(status_code=404, detail="No suitable video found")

@app.get("/download/{token}")
async def download_file(token: str):
    if token not in token_map:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    file_path = token_map.pop(token)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    response = FileResponse(file_path, filename=os.path.basename(file_path), media_type='video/mp4')

    @response.call_on_close
    def cleanup():
        try:
            os.remove(file_path)
        except:
            pass

    return response
