import numpy as np
from PIL import Image, ImageOps
from io import BytesIO
def randomized_svd(matrix, components, oversampling=8):
    rows, cols = matrix.shape
    sample_size = min(
        components + oversampling,
        min(rows, cols)
    )
    rng = np.random.default_rng(42)
    omega = rng.standard_normal((cols, sample_size))
    projected = matrix @ omega
    projected = matrix @ (matrix.T @ projected)
    Q, _ = np.linalg.qr(
        projected,
        mode="reduced"
    )
    small_matrix = Q.T @ matrix
    U_small, S, VT = np.linalg.svd(
        small_matrix,
        full_matrices=False
    )
    U = Q @ U_small[:, :components]
    return U, S[:components], VT[:components, :]
def pca_compress(image, quality_retention=90):
    image = ImageOps.exif_transpose(image).convert("RGB")
    pixels = np.asarray(image, dtype=np.float64)
    height, width, _ = pixels.shape
    max_components = min(128, height, width)
    components = max(
        1,
        round(max_components * quality_retention / 100)
    )
    reconstructed_channels = []
    for channel in range(3):
        matrix = pixels[:, :, channel]
        mean = np.mean(matrix, axis=0)
        centered = matrix - mean
        U, S, VT = randomized_svd(
            centered,
            components
        )
        reconstructed = (U * S) @ VT + mean
        reconstructed_channels.append(reconstructed)
    reconstructed_image = np.stack(
        reconstructed_channels,
        axis=2
    )
    reconstructed_image = np.clip(
        reconstructed_image, 0, 255
    ).astype(np.uint8)
    mse = np.mean(
        (pixels - reconstructed_image.astype(np.float64)) ** 2
    )
    psnr = (
        float("inf")
        if mse == 0
        else 10 * np.log10((255 ** 2) / mse)
    )
    output_image = Image.fromarray(reconstructed_image)
    buffer = BytesIO()
    output_image.save(
        buffer,
        format="WEBP",
        quality=95,
        method=2
    )
    compressed_data = buffer.getvalue()
    preview = Image.open(
        BytesIO(compressed_data)
    ).copy()
    return (
        compressed_data,
        preview,
        mse,
        psnr,
        components
    )