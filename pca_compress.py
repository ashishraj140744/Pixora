import numpy as np
from PIL import Image
from io import BytesIO
def pca_compress(image, components=50):
    image = image.convert("RGB")
    image.thumbnail((256, 256))
    pixels = np.array(image, dtype=np.float64)
    reconstructed_channels = []
    for channel in range(3):
        matrix = pixels[:, :, channel]
        mean = np.mean(matrix, axis=0)
        centered = matrix - mean
        U, S, VT = np.linalg.svd(
            centered,
            full_matrices=False
        )
        k = min(components, len(S))
        compressed = U[:, :k] @ np.diag(S[:k]) @ VT[:k, :]
        reconstructed = compressed + mean
        reconstructed_channels.append(reconstructed)
    reconstructed_image = np.stack(
        reconstructed_channels,
        axis=2
    )
    reconstructed_image = np.clip(
        reconstructed_image, 0, 255
    ).astype(np.uint8)
    original = pixels.astype(np.uint8)
    mse = np.mean(
        (original.astype(float) -
         reconstructed_image.astype(float)) ** 2
    )
    if mse == 0:
        psnr = float("inf")
    else:
        psnr = 10 * np.log10((255 ** 2) / mse)
    output = Image.fromarray(reconstructed_image)
    buffer = BytesIO()
    output.save(buffer, format="PNG")
    return buffer.getvalue(), mse, psnr, output