import streamlit as st
from PIL import Image
from io import BytesIO
st.set_page_config(
    page_title="Pixora - Image Compressor",
    page_icon="🖼️",
    layout="wide"
)
def format_size(size):
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    return f"{size / 1024:.2f} KB"
st.title("🖼️ Pixora")
st.subheader("Intelligent Image Compression")
st.write("Compress your images while maintaining visual quality.")
st.divider()
uploaded_file = st.file_uploader(
    "Upload your image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: JPG, JPEG, PNG and WEBP"
)
if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    image = Image.open(BytesIO(image_bytes))
    file_size = len(image_bytes)
    width, height = image.size
    image_format = image.format or "Unknown"
    st.success("Image uploaded successfully!")
    st.subheader("Original Image")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(image, use_container_width=True)
    with col2:
        st.markdown("### Image Details")
        st.metric("File Size", format_size(file_size))
        st.metric("Width", f"{width} px")
        st.metric("Height", f"{height} px")
        st.write(f"**Format:** {image_format}")
        st.write(f"**File Name:** {uploaded_file.name}")
else:
    st.info("Upload an image to get started.")