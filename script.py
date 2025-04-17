import streamlit as st
from PIL import Image
import os
import io
import zipfile
import tempfile

st.set_page_config(page_title="GIF Frame Extractor", layout="centered")
st.title("🖼️ GIF Frame Extractor")

uploaded_gif = st.file_uploader("Upload a GIF file", type=["gif"])

if uploaded_gif:
    st.subheader("Uploaded GIF Preview")
    st.image(uploaded_gif)

    # Create a temporary directory for extracted frames
    with tempfile.TemporaryDirectory() as temp_dir:
        gif_path = os.path.join(temp_dir, uploaded_gif.name)

        # Save the uploaded GIF to the temp dir
        with open(gif_path, "wb") as f:
            f.write(uploaded_gif.read())

        # Extract frames
        frame_paths = []
        with Image.open(gif_path) as im:
            frame_number = 0
            while True:
                frame = im.copy().convert("RGBA")
                frame_path = os.path.join(temp_dir, f"frame_{frame_number:03d}.png")
                frame.save(frame_path, format="PNG")
                frame_paths.append(frame_path)
                frame_number += 1
                try:
                    im.seek(im.tell() + 1)
                except EOFError:
                    break

        st.subheader(f"Extracted {len(frame_paths)} Frames")

        cols = st.columns(5)
        for i, frame_path in enumerate(frame_paths):
            with open(frame_path, "rb") as f:
                image_bytes = f.read()
            with cols[i % 5]:
                st.image(image_bytes, caption=f"Frame {i}", use_container_width=True)

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for path in frame_paths:
                zipf.write(path, arcname=os.path.basename(path))
        zip_buffer.seek(0)

        st.download_button(
            label="📦 Download All Frames as ZIP",
            data=zip_buffer,
            file_name="gif_frames.zip",
            mime="application/zip"
        )
