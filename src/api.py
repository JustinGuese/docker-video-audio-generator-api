import asyncio
import base64
import glob
import hashlib
from enum import Enum
from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from createVideo import createFullVideo

app = FastAPI(title="video generator api")
# only in memory for now
app.state_storage = dict()


class VideoState(Enum):
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


def getDoneVideos():
    # fill app.state_storage  with existing videos
    for video_file in glob.glob("output/*.mp4"):
        video_id = video_file.split("/")[-1].split(".")[0]
        app.state_storage[video_id] = VideoState.DONE


class VideoRequest(BaseModel):
    script: str
    topic: str = "technology"
    portrait: bool = True


class VideoResponse(BaseModel):
    video_id: str
    state: VideoState


def scriptIdFromScript(script: str) -> str:
    return base64.urlsafe_b64encode(
        hashlib.sha1(script.encode()).digest()[:10]
    ).decode()[:-2]


def async_create_video(script_id, video_request: VideoRequest):
    createFullVideo(
        script_id,
        video_request.script,
        video_request.topic,
        video_request.portrait,
    )
    app.state_storage[script_id] = VideoState.DONE


@app.post("/generate", response_model=VideoResponse)
def generate_video(video_request: VideoRequest):
    script_id = scriptIdFromScript(video_request.script)

    if script_id in app.state_storage:
        raise HTTPException(
            status_code=400,
            detail=f"Video already exists: {script_id}, with state {app.state_storage[script_id]}",
        )

    app.state_storage[script_id] = VideoState.PROCESSING

    thread = Thread(target=async_create_video, args=(script_id, video_request))
    thread.start()

    return VideoResponse(video_id=script_id, state=VideoState.PROCESSING)


@app.post("/get_id_for_script")
def get_id_for_script(script: str):
    script_id = scriptIdFromScript(script)
    return script_id


@app.get("/status/{video_id}", response_model=VideoResponse)
def get_video_status(video_id: str):
    getDoneVideos()
    if video_id not in app.state_storage:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse(video_id=video_id, state=app.state_storage[video_id])


@app.get("/status")
def get_all_videos_status():
    getDoneVideos()
    return app.state_storage


@app.get("/download/{video_id}", response_class=FileResponse)
def download_video(video_id: str):
    getDoneVideos()
    if video_id not in app.state_storage:
        raise HTTPException(status_code=404, detail="Video not found")
    if app.state_storage[video_id] != VideoState.DONE:
        raise HTTPException(status_code=400, detail="Video not ready yet")
    return FileResponse(f"output/{video_id}.mp4")
