import streamlit as st

st.set_page_config(page_title="YT ➜ Twitter Thread Gen", page_icon="🎬", layout="centered")
st.title("🎥 YouTube ➜ 🧵 Twitter Thread Generator")
st.caption("Powered by transcripts + LLM magic (Groq ⚡ Mixtral)")
st.divider()
video_url = st.text_input("🔗 Paste a YouTube video URL")
tone = st.selectbox("💬 Choose the audience tone", ["Boomer", "Gen-Z", "Gen-Alpha"])
generate = st.button("🚀 Generate Twitter Thread")

from transcript_utils import extract_video_id, fetch_transcript_text
from llm_thread_gen import generate_twitter_thread_from_transcript

if generate:
    if not video_url:
        st.warning("Please paste a YouTube URL first.")
    else:
        # Step 1: Extract Video ID
        video_id = extract_video_id(video_url)
        print(video_id)
        
        # Step 2: Get Transcript
        with st.spinner("📜 Fetching transcript..."):
            transcript_text = fetch_transcript_text(video_id)
            
        if not transcript_text or transcript_text.startswith("❌"):
            st.error("No transcript found or video unsupported.")
        else:
            # Step 3: Generate Thread
            with st.spinner(f"🤖 Writing Twitter thread in *{tone}* tone..."):
                twitter_thread = generate_twitter_thread_from_transcript(transcript_text, tone)
                
            st.success("✅ Thread Ready!")
            st.markdown("### 🧵 Generated Twitter Thread:")
            
            # Process the thread correctly
            if twitter_thread.startswith("[ERROR]"):
                st.error(twitter_thread)
            else:
                # Remove the header if present
                if "Generated Twitter Thread:" in twitter_thread:
                    content = twitter_thread.split("Generated Twitter Thread:", 1)[1].strip()
                else:
                    content = twitter_thread
                
                # Split by numbered tweets (1. 2. etc.)
                import re
                tweets = re.split(r'\n\s*\d+\.|\n\s*\d+\)', content)
                tweets = [tweet.strip() for tweet in tweets if tweet.strip()]
                
                # Display each tweet properly
                for i, tweet in enumerate(tweets):
                    st.markdown(f"**Tweet {i+1}:**")
                    st.markdown(f"> {tweet}")
                    st.divider()
            
            st.caption("✨ Now go be a threadboi.")
