import os
import requests
import json
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough

# ✅ Load API key from env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Prompt Template for Twitter Thread Gen
prompt_template = """
You are a top-tier content strategist known for writing highly engaging and informative Twitter threads.

Your audience type is: **{audience_type}**
Adjust the tone, vocabulary, and examples to best match this audience’s preferences.
Given the transcript of a YouTube video, generate a multi-threaded Twitter chain with these characteristics:

🧲 1. Start with a **powerful 1-liner hook** to capture attention.
🧵 2. Create a **chain of 5–8 concise tweets**, each expanding on key insights or concepts from the video.
✨ 3. Format the tweets for **maximum readability and virality**:
    - Use emojis strategically
    - Use bold or CAPS for emphasis
    - Use hooks, numbered lists, or cliffhangers to keep readers scrolling
📣 4. End with a **closing tweet** that summarizes the value or gives a strong CTA (e.g., save, like, share, follow).

Transcript:
{transcript}

Your response should contain each tweet as a **separate line**, exactly how they’d be posted in a Twitter thread.
"""

# ✅ Groq-powered custom LLM class
class GroqLLM(LLM, BaseModel):
    api_key: str = GROQ_API_KEY
    model_name: str = "gemma2-9b-it"
    temperature: float = 0.7
    max_tokens: int = 2048

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

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )

        print("[DEBUG] Raw API Response:", response.text)

        if response.status_code != 200:
            return f"[ERROR] Groq API: {response.status_code} - {response.text}"

        try:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        except json.JSONDecodeError:
            return "[ERROR] Invalid JSON from Groq API"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

# ✅ Final thread generator function
def generate_twitter_thread_from_transcript(transcript_text: str,audience_type:str) -> str:
    if not transcript_text or transcript_text.startswith("❌"):
        return transcript_text

    try:
        llm = GroqLLM()
        prompt = PromptTemplate(template=prompt_template, input_variables=["transcript","audience_type"])
        chain = prompt | llm | RunnablePassthrough()
        thread = chain.invoke({
            "transcript": transcript_text,
            "audience_type": selected_audience
})

        return thread
    except Exception as e:
        return f"[ERROR] LLM processing failed: {str(e)}"
