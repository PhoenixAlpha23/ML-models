import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import nltk
from nltk.corpus import stopwords
from typing import Tuple, List

# Initialize stopwords (only download if needed)
try:
    STOP_WORDS = set(stopwords.words('english'))
except:
    nltk.download('stopwords')
    STOP_WORDS = set(stopwords.words('english'))

# Common filler words to remove
FILLER_WORDS = r'\b(um|uh|like|you know|so|actually|basically|literally)\b'

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

def clean_transcript(text: str) -> str:
    """
    Cleans raw transcript text by:
    - Removing timestamps and speaker labels
    - Eliminating filler words
    - Removing stopwords while preserving sentence structure
    """
    # Remove timestamps and speaker labels
    text = re.sub(r'\[[\d:]+\]|SPEAKER_\d+:', '', text)
    
    # Remove filler words
    text = re.sub(FILLER_WORDS, '', text, flags=re.IGNORECASE)
    
    # Remove stopwords while preserving sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = []
    
    for sentence in sentences:
        words = sentence.split()
        cleaned_words = [word for word in words if word.lower() not in STOP_WORDS]
        if cleaned_words:  # Only add non-empty sentences
            cleaned_sentences.append(' '.join(cleaned_words))
    
    return ' '.join(cleaned_sentences)

def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """
    Splits text into semantically coherent chunks with overlap.
    Preserves sentence boundaries where possible.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            # Keep overlap by retaining last few sentences
            overlap_sentences = min(3, len(current_chunk))  # Keep max 3 sentences for overlap
            current_chunk = current_chunk[-overlap_sentences:] + [sentence]
            current_length = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def fetch_transcript_text(video_id: str, clean: bool = True, chunked: bool = False) -> Tuple[str, List[str]]:
    """
    Fetches and processes YouTube transcript.
    Returns:
    - Tuple of (raw_transcript, cleaned_chunks) if chunked=True
    - Raw transcript string if clean=False and chunked=False
    - Cleaned transcript string if clean=True and chunked=False
    
    Error messages start with ❌
    """
    if not video_id:
        return "❌ Invalid video ID.", []
    
    try:
        print(f"[DEBUG] Fetching transcript for video ID: {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        raw_text = " ".join([entry['text'] for entry in transcript])
        
        if not clean and not chunked:
            return raw_text, []
        
        cleaned_text = clean_transcript(raw_text)
        
        if not chunked:
            return cleaned_text, []
        
        chunks = chunk_text(cleaned_text)
        return raw_text, chunks
        
    except TranscriptsDisabled:
        return "❌ Transcripts are disabled for this video.", []
    except NoTranscriptFound:
        return "❌ No transcript found (not available in English or at all).", []
    except VideoUnavailable:
        return "❌ Video is unavailable.", []
    except Exception as e:
        print(f"[DEBUG] Exception details: {type(e).__name__}: {str(e)}")
        return f"❌ Unexpected error: {str(e)}", []
