import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

def extract_video_id(url: str) -> str:
    """
    Extracts YouTube video ID from standard or shortened URLs.
    """
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        video_id = parsed.path.lstrip('/')
    elif 'youtube.com' in parsed.netloc:
        video_id = parse_qs(parsed.query).get('v', [None])[0]
    else:
        video_id = None

    print(f"[DEBUG] Extracted Video ID: {video_id}")
    return video_id


def fetch_transcript_text(video_id: str) -> str:
    """
    Fetches and formats the transcript text for a YouTube video.
    Returns plain caption text or error message string starting with ❌
    """
    if not video_id:
        return "❌ Invalid video ID."

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text

    except TranscriptsDisabled:
        return "❌ Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "❌ No transcript found (not available in English or at all)."
    except VideoUnavailable:
        return "❌ Video is unavailable."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
