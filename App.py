import streamlit as st
import yt_dlp
import os
import tempfile

# Page Config
st.set_page_config(page_title="VP Twitter Downloader", page_icon="⬇️")

# --- CHANGED TITLE HERE ---
st.title("⬇️ VP Twitter Broadcast Downloader")
st.write("Paste a Twitter/X broadcast link below.")

# Input
url = st.text_input("Video URL")

def download_video(link):
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = 0.0
                # Method 1: Calculate by Bytes (Standard videos)
                if d.get('total_bytes') or d.get('total_bytes_estimate'):
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    p = downloaded / total
                
                # Method 2: Calculate by Fragments (Twitter Broadcasts/HLS)
                # This fixes the "Grey Bar" issue
                elif d.get('fragment_index') and d.get('fragment_count'):
                    current = d.get('fragment_index')
                    total_frags = d.get('fragment_count')
                    p = current / total_frags

                # Update the UI
                clean_p = max(0.0, min(1.0, p))
                progress_bar.progress(clean_p)
                status_text.text(f"Downloading: {int(clean_p * 100)}%")
                
            except Exception:
                pass # Keep going if calculation fails slightly
                
        elif d['status'] == 'finished':
            status_text.text("Processing video... (Stitching chunks)")
            progress_bar.progress(1.0)

    # Use a temporary directory for cloud stability
    with tempfile.TemporaryDirectory() as tmpdirname:
        
        ydl_opts = {
            'outtmpl': f'{tmpdirname}/%(title).50s.%(ext)s',
            'restrictfilenames': True,
            'concurrent_fragment_downloads': 4,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                
                # Read into memory
                with open(filename, "rb") as f:
                    return f.read(), os.path.basename(filename)
                    
        except Exception as e:
            st.error(f"Error: {e}")
            return None, None

# Button
if st.button("Download Video"):
    if url:
        with st.spinner('Downloading...'):
            video_data, video_name = download_video(url)
            
            if video_data:
                st.success("Success! Click below to save.")
                st.download_button(
                    label="💾 Save Video",
                    data=video_data,
                    file_name=video_name,
                    mime="video/mp4"
                )
    else:
        st.warning("Please paste a URL first.")
