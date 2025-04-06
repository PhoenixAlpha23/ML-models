import os
import requests
import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate

# Load API key from env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Improved prompt with clearer formatting instructions
prompt_template = """
You are a top-tier content strategist known for writing highly engaging and informative Twitter threads.
Your audience type is: **{audience_type}**
Adjust the tone, vocabulary, and examples to best match this audience's preferences.

Based on this video transcript, create a compelling Twitter thread:

{transcript}

FORMAT YOUR RESPONSE AS FOLLOWS:
1. Start with a powerful hook tweet
2. Include 5-8 concise, informative tweets that highlight key insights
3. End with a strong closing tweet or call to action
4. Number each tweet (1. 2. 3. etc.)
5. Use emojis strategically to enhance readability
6. Make each tweet complete and impactful

IMPORTANT: Each tweet must be complete, coherent, and valuable on its own. Avoid repetition or partial thoughts.
"""

class GroqLLM(LLM, BaseModel):
    api_key: str = Field(default=GROQ_API_KEY)
    model_name: str = Field(default="llama3-70b-8192")  # Changed to llama3-70b for better quality
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1024)
    
    @property
    def _llm_type(self) -> str:
        return "groq"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Ensure transcript isn't too long for context window
        if len(prompt) > 12000:
            prompt = prompt[:12000] + "...[truncated for length]"
        
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
                timeout=60  # Added timeout
            )
            
            print(f"[DEBUG] Status Code: {response.status_code}")
            if response.status_code != 200:
                return f"[ERROR] Groq API: {response.status_code} - {response.text[:500]}"
            
            response_json = response.json()
            raw_thread = response_json["choices"][0]["message"]["content"]
            
            # Post-process to clean up the thread
            return self._clean_thread(raw_thread)
            
        except requests.exceptions.RequestException as e:
            return f"[ERROR] Request failed: {str(e)}"
        except json.JSONDecodeError:
            return "[ERROR] Invalid JSON from Groq API"
        except Exception as e:
            return f"[ERROR] Unexpected error: {str(e)}"
    
    def _clean_thread(self, raw_thread: str) -> str:
        """Clean and format the generated thread"""
        # Split by numbered format (1. 2. etc)
        tweets = re.split(r'\n\s*\d+\.|\n\s*\d+\)', raw_thread)
        
        # Remove empty items and strip whitespace
        tweets = [tweet.strip() for tweet in tweets if tweet.strip()]
        
        # Reconstruct with proper numbering and filtering obviously incomplete tweets
        clean_tweets = []
        for i, tweet in enumerate(tweets):
            # Skip very short tweets or obviously incomplete ones
            if len(tweet) < 10 or tweet.count('.') == 0:
                continue
                
            # Skip tweets that are duplicates or substrings of previous tweets
            if any(tweet in prev_tweet for prev_tweet in clean_tweets):
                continue
                
            clean_tweets.append(f"{i+1}. {tweet}")
            
            # Limit to 9 tweets maximum (hook + 7 body + conclusion)
            if len(clean_tweets) >= 9:
                break
                
        return "\n\n".join(clean_tweets)
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

def generate_twitter_thread_from_transcript(transcript_text: str, tone: str) -> str:
    if not transcript_text or transcript_text.startswith("❌"):
        return transcript_text
        
    try:
        # Limit transcript length
        max_length = 10000
        if len(transcript_text) > max_length:
            transcript_text = transcript_text[:max_length] + "...[truncated]"
            
        # Initialize LLM with improved parameters    
        llm = GroqLLM(
            model_name="llama3-70b-8192",  # More capable model
            temperature=0.7,
            max_tokens=1024
        )
        
        # Create prompt
        prompt = PromptTemplate(template=prompt_template, input_variables=["transcript", "audience_type"])
        
        # Generate thread
        formatted_prompt = prompt.format(transcript=transcript_text, audience_type=tone)
        thread = llm(formatted_prompt)
        
        # Format output for display
        if thread and not thread.startswith("[ERROR]"):
            return "✅ Thread Ready!\n\n🧵 Generated Twitter Thread:\n" + thread
        else:
            return thread
            
    except Exception as e:
        return f"[ERROR] LLM processing failed: {str(e)}"
