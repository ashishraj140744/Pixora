import streamlit as st
from PIL import Image
from io import BytesIO
from smart_compress import compress_image
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
    st.divider()
    st.subheader("Smart Compress")
    target_kb = st.slider(
        "Target file size (KB)",
        min_value=10,
        max_value=2000,
        value=200,
        step=10
    )
    output_format = st.selectbox(
        "Output Format",
        ["JPEG", "WEBP"]
    )
    if st.button("Compress Image", type="primary"):
        compressed_data = compress_image(
            image,
            target_kb,
            output_format
        )
        compressed_size = len(compressed_data)
        st.session_state["compressed_data"] = compressed_data
        st.session_state["compressed_size"] = compressed_size
        st.session_state["output_format"] = output_format
    if "compressed_data" in st.session_state:
        compressed_data = st.session_state["compressed_data"]
        compressed_size = st.session_state["compressed_size"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(image, use_container_width=True)
            st.write(f"Size: {format_size(file_size)}")
        with col2:
            st.subheader("Compressed")
            st.image(compressed_data, use_container_width=True)
            st.write(f"Size: {format_size(compressed_size)}")
        if compressed_size <= target_kb * 1024:
            st.success("Target size achieved!")
        else:
            st.warning("Target size could not be reached.")
        reduction = (1 - compressed_size / file_size) * 100
        st.metric("Size Reduction", f"{reduction:.2f}%")
        extension = "jpg" if output_format == "JPEG" else "webp"
        st.download_button(
            "Download Compressed Image",
            data=compressed_data,
            file_name=f"pixora_compressed.{extension}",
            mime=f"image/{extension}"
        )
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