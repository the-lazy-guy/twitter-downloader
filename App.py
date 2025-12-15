import streamlit as st
import yt_dlp
import os
import time

# Page Config
st.set_page_config(page_title="Twitter Downloader", page_icon="⬇️")

st.title("⬇️ Internal Video Downloader")
st.write("Paste a Twitter/X broadcast link below.")

# Input
url = st.text_input("Video URL")

# Logic
def download_video(link):
    # Create placeholders for the UI elements
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # --- THE FIX IS HERE ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                # 1. Get total bytes (sometimes it's an estimate for streams)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                
                if total_bytes:
                    # 2. Calculate percentage manually
                    percentage = downloaded_bytes / total_bytes
                    
                    # 3. Update Streamlit UI
                    # Ensure percentage is between 0.0 and 1.0
                    clean_percent = max(0.0, min(1.0, percentage))
                    progress_bar.progress(clean_percent)
                    
                    # Show nice text status (e.g., "15MB / 50MB")
                    status_text.text(f"Downloading: {int(clean_percent * 100)}%")
                else:
                    # Fallback if total size is unknown (common in live streams)
                    status_text.text(f"Downloading: {downloaded_bytes / 1024 / 1024:.2f} MB collected...")
            except Exception as e:
                print(f"Progress Error: {e}") # Log to console just in case
                
        elif d['status'] == 'finished':
            status_text.text("Processing video... (Stitching chunks)")
            progress_bar.progress(1.0)

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s', 
        'concurrent_fragment_downloads': 15,
        'progress_hooks': [progress_hook], # Connect our fixed hook
        'quiet': True,
        'no_warnings': True
    }

    try:
        # Create folder if not exists
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Button
if st.button("Download Video"):
    if url:
        with st.spinner('Starting download engine...'):
            file_path = download_video(url)
            
            if file_path and os.path.exists(file_path):
                st.success(f"Done! Ready to save.")
                
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="💾 Save to my Computer",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
    else:
        st.warning("Please paste a URL first.")