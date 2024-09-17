import urllib.request
from os import environ
from pathlib import Path

import requests
from tqdm import tqdm

USERAGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"


# saves videos to videos/{topic} folder
def downloadVideosForTopic(
    topic: str,
    count: int = 10,
):

    params = {
        "query": topic,
        "per_page": count,
        "key": environ["PIXABAY_API_KEY"],
    }
    req = requests.get("https://pixabay.com/api/videos/", params=params)
    req.raise_for_status()
    search_videos = req.json()["hits"]

    Path(f"videos/{topic}").mkdir(parents=True, exist_ok=True)
    for hit in tqdm(search_videos):
        video_url = hit["videos"]["large"]["url"]
        video_id = hit["id"]
        video_path = f"videos/{topic}/{video_id}.mp4"
        headers = {"User-Agent": USERAGENT}
        req = urllib.request.Request(video_url, headers=headers)
        with urllib.request.urlopen(req) as response, open(
            video_path, "wb"
        ) as out_file:
            data = response.read()
            out_file.write(data)


if __name__ == "__main__":
    vids = downloadVideosForTopic("technology")
