import logging
from pathlib import Path
from random import shuffle

from moviepy.editor import VideoFileClip, concatenate_videoclips

from downloadVideo import downloadVideosForTopic


def getVideos(topic: str) -> list[str]:
    # if videos/{topic} folder does not exist, download videos
    if not Path(f"videos/{topic}").exists():
        logging.info(f"Downloading videos for {topic} as they were not found on disk")
        downloadVideosForTopic(topic)
    return [str(x) for x in Path(f"videos/{topic}").rglob("*.mp4")]


def createVideo(
    topic: str,
    length_seconds: float,
    seconds_per_video: int = 5,
) -> VideoFileClip:
    howManyRequired = int(length_seconds // seconds_per_video) + 1
    videos = getVideos(topic)
    # repeat videos until we have enough to fill the length
    repetitions = howManyRequired // len(videos) + 1
    videos = videos * repetitions
    videos = videos[:howManyRequired]
    # shuffle the videos
    shuffle(videos)

    clips = []
    for video in videos:
        clip = VideoFileClip(video).subclip(0, seconds_per_video)
        clips.append(clip)
    clips = concatenate_videoclips(clips, method="chain")
    return clips


if __name__ == "__main__":
    print(createVideo("technology", 10.2))
