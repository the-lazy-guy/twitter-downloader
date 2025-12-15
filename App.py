import streamlit as st
import yt_dlp
import os
import tempfile # <--- New import for safe cloud file handling

# Page Config
st.set_page_config(page_title="Twitter Downloader", page_icon="⬇️")

st.title("⬇️ Internal Video Downloader")
st.write("Paste a Twitter/X broadcast link below.")

# Input
url = st.text_input("Video URL")

def download_video(link):
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    p = downloaded / total
                    progress_bar.progress(max(0.0, min(1.0, p)))
                    status_text.text(f"Downloading: {int(p * 100)}%")
                else:
                    status_text.text("Downloading stream...")
            except:
                pass
        elif d['status'] == 'finished':
            status_text.text("Processing video... (Stitching chunks)")
            progress_bar.progress(1.0)

    # Use a temporary directory that is guaranteed to be writable and clean
    with tempfile.TemporaryDirectory() as tmpdirname:
        
        # Configure yt-dlp for CLOUD reliability
        ydl_opts = {
            'outtmpl': f'{tmpdirname}/%(title).50s.%(ext)s', # Use temp folder + Short name
            'restrictfilenames': True,  # Remove emojis/spaces that break Linux paths
            'concurrent_fragment_downloads': 4, # LOWERED from 15 to 4 for server stability
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                
                # We must read the file into memory to serve it, 
                # because the temp folder disappears when this function ends.
                with open(filename, "rb") as f:
                    return f.read(), os.path.basename(filename)
                    
        except Exception as e:
            st.error(f"Error: {e}")
            return None, None

# Button
if st.button("Download Video"):
    if url:
        with st.spinner('Downloading... (This may take a minute)'):
            # Get the file data directly into memory
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
