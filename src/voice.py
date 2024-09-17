from edge_tts import Communicate
from moviepy.editor import AudioFileClip


def generateVoice(
    text: str, outputfile: str, voice: str = "en-GB-SoniaNeural"
) -> AudioFileClip:
    communicate = Communicate(text, voice)
    communicate.save_sync(outputfile)
    return AudioFileClip(outputfile)


if __name__ == "__main__":
    generateVoice("Hello, this is a voice test. I am Sonia!")
