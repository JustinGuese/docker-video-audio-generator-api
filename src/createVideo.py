import logging
import os
from pathlib import Path
from subprocess import PIPE, Popen, check_call
from time import sleep

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.editor import AudioFileClip, VideoFileClip

from subtitle import createTranscript
from video import createVideo
from voice import generateVoice

BACKGROUNDAUDIO_VOLUME = 0.4


def makeVideoSmaller(filename: str, cwd: str = "./"):
    cmd = f"mv {filename} {filename.replace('.mp4', '_big.mp4')}"
    check_call(cmd, shell=True)

    cmd = f"ffmpeg -y -i {filename.replace('.mp4', '_big.mp4')} -vcodec libx265 -crf 28 {filename}"
    p = Popen(cmd, stdout=PIPE, shell=True)
    (output, err) = p.communicate()
    # This makes the wait possible
    while p.wait() is None:
        sleep(5)
        logging.debug("waiting for ffmpeg to finish...")

    cmd = f"rm {filename.replace('.mp4', '_big.mp4')}"
    check_call(cmd.split())


def addSubtitlesToVideo(videoPath: str, subtitlePath: str):
    cmd = f"ffmpeg -i {videoPath} -vf subtitles={subtitlePath} {videoPath.replace('workdir', 'output')}"
    check_call(cmd, shell=True)


def createFullVideo(
    script_id: str, script: str, topic: str = "technology", portrait: bool = True
):

    Path("workdir").mkdir(parents=True, exist_ok=True)
    Path("videos").mkdir(parents=True, exist_ok=True)
    Path("output").mkdir(parents=True, exist_ok=True)

    baseFileName = "workdir/" + script_id
    videoFileName = baseFileName + ".mp4"
    audioFileName = baseFileName + ".mp3"
    subtitleFileName = baseFileName + ".srt"

    if os.path.exists(videoFileName):
        logging.info(f"Video {videoFileName} already exists, load instead")
        scriptAudioClip = AudioFileClip(audioFileName)
    else:
        scriptAudioClip: AudioFileClip = generateVoice(script, audioFileName)

    if os.path.exists(videoFileName):
        logging.info(f"Video {videoFileName} already exists, load instead")
        videoClip = VideoFileClip(videoFileName)
    else:
        videoClip: VideoFileClip = createVideo(topic, scriptAudioClip.duration)
        backgroundMusic = (
            AudioFileClip("background_music.mp3")
            .volumex(BACKGROUNDAUDIO_VOLUME)
            .subclip(0, scriptAudioClip.duration)
        )

        fullAudio = CompositeAudioClip([scriptAudioClip, backgroundMusic])
        videoClip = videoClip.set_audio(fullAudio)

        if portrait:
            videoClip = videoClip.resize(height=1920)
            videoClip = videoClip.crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
        cpuCores = os.cpu_count()
        videoClip.write_videofile(
            videoFileName,
            codec="libx264",
            audio_codec="aac",
            threads=cpuCores * 4,
            fps=24,
        )

        # moviepy tends to create quite big files, make them smaller using ffmpeg
        makeVideoSmaller(videoFileName)

    # next generate .srt
    if os.path.exists(subtitleFileName):
        logging.info(f"Subtitle {subtitleFileName} already exists, load instead")
    else:
        createTranscript(audioFileName)

    # add .srt to video, this command also moves file to output folder
    addSubtitlesToVideo(videoFileName, subtitleFileName)


if __name__ == "__main__":
    script = """Adobe is set to enhance video editing with the upcoming Firefly Video Model, streamlining creative workflows in Premiere Pro. Mistral's launch of the Pixtral 12B multimodal model marks a significant advance in AI capabilities, particularly for those looking to integrate image and text processing. In fashion AI, a new dataset focusing on personalization strategies promises to refine outfit recommendations based on individual styles and occasions. Meanwhile, advancements in 3D scene reconstruction and the introduction of Hierarchical Context Merging (HOMER) suggest groundbreaking potential for large language models. Amazon Web Services has rolled out a comprehensive AI stack for serverless applications, perfect for developers aiming to leverage powerful LLMs. Additionally, Musk's claims regarding Tesla and xAI signal a competitive edge in the AI landscape, while OpenAI's pursuit of $6.5B funding reflects the booming demand for AI solutions. For those in the AI industry, the recommendation is clear: stay informed about these emerging tools and models to enhance product offerings and maintain competitive advantages. Explore these developments now to harness their potential for your projects."""
    createFullVideo("ApnJY3tXITXxQg", script, "technology")
