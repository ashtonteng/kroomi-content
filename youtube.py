import math
import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build


def extract_youtube_video_id(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Check if the domain is 'youtu.be' (shortened URL)
    if parsed_url.netloc == 'youtu.be':
        # The video ID is the path component in the shortened URL
        return parsed_url.path[1:]  # Removing the leading '/'

    # Check if the domain is 'www.youtube.com' (full URL)
    elif parsed_url.netloc == 'www.youtube.com':
        # Parse the query string
        query_string = parse_qs(parsed_url.query)
        # The video ID is under the 'v' key in the query string
        video_id = query_string.get('v')
        if video_id:
            return video_id[0]

    # In case of an invalid or different kind of URL
    raise ValueError(f'Invalid YouTube URL: {url}')


def get_metadata_youtube_video(video_id: str) -> dict:
    youtube_api_key = os.getenv('YOUTUBE_DATA_API_V3_API_KEY')
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    # print(json.dumps(response, indent=4))
    if response['items']:
        title = response['items'][0]['snippet']['title']
        description = response['items'][0]['snippet']['description']
        channel = response['items'][0]['snippet']['channelTitle']
        # get the first paragraph of the description only
        # TODO: summarize with GPT
        description = description.split('\n')[0]
        return {
            'title': title,
            'description': description,
            'channel': channel
        }
    else:
        raise Exception('No video found')


def get_transcript_from_youtube_video(video_id: str) -> str:
    video_transcript = YouTubeTranscriptApi.get_transcript(video_id)
    output = ''
    for x in video_transcript:
        sentence = x['text']
        start = math.floor(float(x['start']))
        output += f'{sentence} ({start})\n'
    return output
