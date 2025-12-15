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
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # Progress hook to update UI
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                progress_bar.progress(float(p) / 100)
                status_text.text(f"Downloading: {d.get('_percent_str')}...")
            except:
                pass
        if d['status'] == 'finished':
            status_text.text("Processing video... (Stitching chunks)")
            progress_bar.progress(1.0)

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s', # Save to a folder
        'concurrent_fragment_downloads': 15,       # SPEED BOOST
        'progress_hooks': [progress_hook],
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
                
                # Create a download button so the user can save it to their PC
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="💾 Save to my Computer",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
    else:
        st.warning("Please paste a URL first.")