import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
import hashlib
from pca_compress import pca_compress
from smart_compress import smart_compress
st.set_page_config(
    page_title="Pixora | Image Compressor",
    page_icon="🖼️",
    layout="wide"
) 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}
.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.brand {
    padding: 12px 0 22px 0;
}
.brand-name {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -2px;
    line-height: 1.1;
}
.brand-tagline {
    font-size: 0.95rem;
    opacity: 0.65;
    margin-top: 7px;
}
[data-testid="stFileUploader"] {
    border: 2px dashed var(--primary-color);
    border-radius: 14px;
    padding: 18px;
    background: var(--secondary-background-color);
}
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border-radius: 12px;
    padding: 15px;
}
div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 9px;
    font-weight: 700;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-top: 15px;
    margin-bottom: 8px;
}
.method-description {
    opacity: 0.75;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)
def format_size(size):
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    return f"{size / 1024:.2f} KB"
st.markdown("""
<div class="brand">
    <div class="brand-name">Pixora.</div>
    <div class="brand-tagline">
        Less weight. More room for creativity.
    </div>
</div>
""", unsafe_allow_html=True)
st.divider()
st.markdown(
    '<div class="section-title">Your image, ready to optimize.</div>',
    unsafe_allow_html=True
)
st.write("Upload an image to get started.")
uploaded_file = st.file_uploader(
    "Drop your image here or browse files",
    type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file is None:
    st.info("Supported formats: JPG, JPEG, PNG and WebP.")
    st.stop()
image_bytes = uploaded_file.getvalue()
image_hash = hashlib.md5(image_bytes).hexdigest()
image = Image.open(
    BytesIO(image_bytes)
)
image = ImageOps.exif_transpose(image).convert("RGB")
original_size = len(image_bytes)
original_width, original_height = image.size
if st.session_state.get("image_hash") != image_hash:
    st.session_state["image_hash"] = image_hash
    st.session_state.pop("compression_result", None)
st.success("Image uploaded successfully.")
st.caption(
    f"Original dimensions: {original_width} × {original_height} pixels"
)
st.divider()
st.markdown(
    '<div class="section-title">Choose your compression method</div>',
    unsafe_allow_html=True
)
method = st.radio(
    "Compression method",
    ["PCA Compressor", "Smart Compressor"],
    horizontal=True
)
if method == "PCA Compressor":
    st.markdown("### Principal Component Analysis")
    st.markdown("""
    <div class="method-description">
    PCA reconstructs an image using fewer principal components.
    This reduces image information and can cause blur or loss of
    fine details. Higher quality retention generally produces
    a clearer reconstruction.
    </div>
    """, unsafe_allow_html=True)
    quality_retention = st.slider(
        "Quality Retention",
        min_value=10,
        max_value=90,
        value=90,
        step=5,
        format="%d%%"
    )
    st.caption(
        "90% retains more image information. "
        "10% retains much less and can produce visible distortion."
    )
    settings = (
        image_hash,
        method,
        quality_retention
    )
    if st.button("Compress with PCA", type="primary"):
        with st.spinner("Reconstructing your image using PCA..."):
            (
                compressed_data,
                preview,
                mse,
                psnr,
                components
            ) = pca_compress(
                image,
                quality_retention
            )
            st.session_state["compression_result"] = {
                "settings": settings,
                "data": compressed_data,
                "preview": preview,
                "mse": mse,
                "psnr": psnr,
                "components": components,
                "quality": None,
                "target_achieved": None,
                "format": "WEBP"
            }
else:
    st.markdown("### Smart Image Compression")
    st.markdown("""
    <div class="method-description">
    Smart Compression adjusts JPEG or WebP encoding quality
    to approach your requested file size. It preserves the
    original pixel dimensions, although encoding may introduce
    compression artifacts.
    </div>
    """, unsafe_allow_html=True)
    output_format = st.selectbox(
        "Output format",
        ["WEBP", "JPEG"]
    )
    size_unit = st.radio(
        "Target size unit",
        ["KB", "MB"],
        horizontal=True
    )
    unit_bytes = (
        1024 if size_unit == "KB"
        else 1024 * 1024
    )
    original_size_in_unit = original_size / unit_bytes
    minimum_target = (
        1.0 if size_unit == "KB"
        else 0.01
    )
    if original_size_in_unit < minimum_target:
        st.warning(
            "The original image is too small for this target-size "
            "setting. Select KB instead."
        )
        target_kb = None
    else:
        step = (
            1.0 if size_unit == "KB"
            else 0.01
        )
        default_target = max(
            minimum_target,
            original_size_in_unit * 0.8
        )
        default_target = min(
            default_target,
            original_size_in_unit
        )
        target_amount = st.number_input(
            f"Target file size ({size_unit})",
            min_value=float(minimum_target),
            max_value=float(original_size_in_unit),
            value=float(default_target),
            step=float(step)
        )
        target_kb = (
            target_amount
            if size_unit == "KB"
            else target_amount * 1024
        )
        st.caption(
            f"Original image size: {format_size(original_size)}. "
            f"Maximum target: {format_size(original_size)}."
        )
    settings = (
        image_hash,
        method,
        output_format,
        target_kb
    )
    if target_kb is not None:
        if st.button("Smart Compress Image", type="primary"):
            with st.spinner("Optimizing image quality..."):
                (
                    compressed_data,
                    preview,
                    quality,
                    target_achieved
                ) = smart_compress(
                    image,
                    target_kb,
                    output_format
                )
                st.session_state["compression_result"] = {
                    "settings": settings,
                    "data": compressed_data,
                    "preview": preview,
                    "mse": None,
                    "psnr": None,
                    "components": None,
                    "quality": quality,
                    "target_achieved": target_achieved,
                    "format": output_format
                }
result = st.session_state.get("compression_result")
if result is not None and result["settings"] == settings:
    compressed_data = result["data"]
    compressed_image = result["preview"]
    compressed_size = len(compressed_data)
    new_width, new_height = compressed_image.size
    reduction = (
        (original_size - compressed_size) / original_size
    ) * 100
    st.divider()
    st.markdown(
        '<div class="section-title">Compression results</div>',
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Original size",
            format_size(original_size)
        )
    with col2:
        st.metric(
            "New size",
            format_size(compressed_size)
        )
    with col3:
        st.metric(
            "Size reduction",
            f"{reduction:.2f}%"
        )
    if reduction > 0:
        st.success("Your image is now smaller.")
    elif reduction == 0:
        st.info("The file size remained unchanged.")
    else:
        st.warning(
            "The output is larger than the original. "
            "This can happen with already optimized images."
        )
    if result["target_achieved"] is False:
        st.warning(
            "The requested target could not be reached even "
            "at the lowest available encoding quality."
        )
    st.divider()
    st.markdown("### Before and After")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original Image**")
        st.image(image, use_container_width=True)
        st.caption(
            f"{original_width} × {original_height} pixels"
        )
    with col2:
        st.markdown("**Compressed Image**")
        st.image(compressed_image, use_container_width=True)
        st.caption(
            f"{new_width} × {new_height} pixels"
        )
    if (original_width, original_height) == (new_width, new_height):
        st.success("Original pixel dimensions preserved.")
    else:
        st.error("The output dimensions do not match the original.")
    st.divider()
    if method == "PCA Compressor":
        st.markdown("### PCA Quality Metrics")
        metric1, metric2, metric3 = st.columns(3)
        with metric1:
            st.metric("MSE", f"{result['mse']:.2f}")
        with metric2:
            st.metric("PSNR", f"{result['psnr']:.2f} dB")
        with metric3:
            st.metric(
                "Components retained",
                str(result["components"])
            )
    else:
        st.markdown("### Encoding Details")
        st.metric(
            "Encoding quality",
            f"{result['quality']} / 95"
        )
    extension = (
        "jpg" if result["format"] == "JPEG"
        else "webp"
    )
    mime_type = (
        "image/jpeg" if extension == "jpg"
        else "image/webp"
    )
    st.download_button(
        "Download Compressed Image",
        data=compressed_data,
        file_name=f"pixora_compressed.{extension}",
        mime=mime_type,
        type="primary"
    )