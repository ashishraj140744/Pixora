import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np
from PIL import Image, ImageOps
from io import BytesIO
def randomized_svd(matrix, components, oversampling=8):
    rows, cols = matrix.shape
    sample_size = min(
        components + oversampling,
        rows,
        cols
    )
    rng = np.random.default_rng(42)
    omega = rng.standard_normal(
        (cols, sample_size),
        dtype=np.float32
    )
    Q, _ = np.linalg.qr(
        matrix @ omega,
        mode="reduced"
    )
    Q, _ = np.linalg.qr(
        matrix @ (matrix.T @ Q),
        mode="reduced"
    )
    U_small, S, VT = np.linalg.svd(
        Q.T @ matrix,
        full_matrices=False
    )
    U = Q @ U_small[:, :components]
    return U, S[:components], VT[:components, :]
def pca_compress(image, quality_retention=90):
    image = ImageOps.exif_transpose(image).convert("RGB")
    pixels = np.asarray(image, dtype=np.uint8)
    height, width, _ = pixels.shape
    max_components = min(128, height, width)
    components = max(
        1,
        round(max_components * quality_retention / 100)
    )
    reconstructed_image = np.empty_like(pixels)
    squared_error = 0.0
    for channel in range(3):
        matrix = pixels[:, :, channel].astype(np.float32)
        mean = matrix.mean(axis=0)
        matrix -= mean
        U, S, VT = randomized_svd(
            matrix,
            components
        )
        reconstructed = (U * S) @ VT
        reconstructed += mean
        np.clip(
            reconstructed,
            0,
            255,
            out=reconstructed
        )
        reconstructed_image[:, :, channel] = reconstructed
        del reconstructed, U, S, VT
        matrix[:] = pixels[:, :, channel]
        matrix -= reconstructed_image[:, :, channel]
        np.square(matrix, out=matrix)
        squared_error += np.sum(
            matrix,
            dtype=np.float64
        )
        del matrix
    mse = squared_error / pixels.size
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