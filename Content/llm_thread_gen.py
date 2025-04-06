import os
import requests
import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate

# Load API key from env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Enhanced prompt template with chunk support
prompt_template = """
You are a top-tier content strategist writing Twitter threads for **{audience_type}** audience.
Current context: {context_note}

Transcript portion:
{transcript}

FORMAT RULES:
1. Start with a powerful hook tweet
2. Include {tweet_count} concise, numbered tweets (1. 2. 3. ...)
3. End with a strong closer/call-to-action
4. Use emojis strategically
5. Make each tweet stand alone

IMPORTANT: If continuing a thread, maintain flow from previous tweets.
"""

class GroqLLM(LLM, BaseModel):
    api_key: str = Field(default=GROQ_API_KEY)
    model_name: str = Field(default="llama3-70b-8192")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1024)
    chunk_processing: bool = Field(default=False)
    
    @property
    def _llm_type(self) -> str:
        return "groq"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                return f"[ERROR] API: {response.status_code} - {response.text[:200]}"
            
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"[ERROR] Request failed: {str(e)}"
    
    def _clean_thread(self, raw_thread: str) -> str:
        """Optimized cleaning logic"""
        tweets = re.split(r'\n\s*\d+[\.\)]', raw_thread)
        tweets = [t.strip() for t in tweets if t.strip() and len(t.split()) > 3]
        
        # Deduplication using set
        unique_tweets = []
        seen = set()
        for i, tweet in enumerate(tweets):
            simplified = re.sub(r'\W+', '', tweet.lower())
            if simplified not in seen:
                seen.add(simplified)
                unique_tweets.append(f"{i+1}. {tweet}")
                if len(unique_tweets) >= 9:
                    break
                    
        return "\n\n".join(unique_tweets)

def generate_twitter_thread_from_transcript(
    transcript_text: str,
    tone: str,
    chunked: bool = False
) -> str:
    """
    Enhanced version supporting:
    - Chunked processing (when chunked=True)
    - Better error handling
    - Configurable tweet count
    """
    if not transcript_text or transcript_text.startswith("❌"):
        return transcript_text
        
    try:
        llm = GroqLLM(
            model_name="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1024,
            chunk_processing=chunked
        )
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["transcript", "audience_type", "context_note", "tweet_count"]
        )
        
        if chunked and isinstance(transcript_text, tuple):
            # Process chunks sequentially with context carryover
            return _process_chunked_transcript(transcript_text, tone, llm, prompt)
        else:
            # Original single-pass processing
            formatted_prompt = prompt.format(
                transcript=transcript_text[:10000],
                audience_type=tone,
                context_note="Full transcript",
                tweet_count="5-8"
            )
            thread = llm(formatted_prompt)
            return _format_output(thread)
            
    except Exception as e:
        return f"[ERROR] Processing failed: {str(e)}"

def _process_chunked_transcript(
    chunks: Tuple[str, List[str]],
    tone: str,
    llm: GroqLLM,
    prompt: PromptTemplate
) -> str:
    """Handle chunked transcript processing"""
    raw_text, chunk_list = chunks
    full_thread = []
    
    for i, chunk in enumerate(chunk_list):
        context_note = (
            f"Part {i+1}/{len(chunk_list)} of transcript"
            if i > 0 else 
            "Beginning of transcript"
        )
        
        response = llm(prompt.format(
            transcript=chunk,
            audience_type=tone,
            context_note=context_note,
            tweet_count="3-5"  # Fewer tweets per chunk
        ))
        
        if not response.startswith("[ERROR]"):
            full_thread.append(llm._clean_thread(response))
            
    return _format_output("\n\n".join(full_thread))

def _format_output(thread: str) -> str:
    """Consistent output formatting"""
    if thread.startswith("[ERROR]"):
        return thread
    return f"✅ Thread Ready!\n\n🧵 Generated Twitter Thread:\n{thread}"
