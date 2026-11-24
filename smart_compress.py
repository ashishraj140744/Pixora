from PIL import Image
from io import BytesIO
def compress_image(image, target_kb, output_format="JPEG"):
    target_bytes = target_kb * 1024
    if output_format == "JPEG":
        image = image.convert("RGB")
    elif output_format == "WEBP":
        image = image.convert("RGB")
    best_image = None
    best_size = float("inf")
    low = 10
    high = 95
    while low <= high:
        quality = (low + high) // 2
        buffer = BytesIO()
        if output_format == "JPEG":
            image.save(
                buffer,
                format="JPEG",
                quality=quality,
                optimize=True
            )
        else:
            image.save(
                buffer,
                format="WEBP",
                quality=quality,
                method=6
            )
        compressed_data = buffer.getvalue()
        compressed_size = len(compressed_data)
        if compressed_size <= target_bytes:
            if target_bytes - compressed_size < target_bytes - best_size:
                best_image = compressed_data
                best_size = compressed_size
            low = quality + 1
        else:
            high = quality - 1
    if best_image is None:
        buffer = BytesIO()
        if output_format == "JPEG":
            image.save(buffer, format="JPEG", quality=10, optimize=True)
        else:
            image.save(buffer, format="WEBP", quality=10, method=6)
        best_image = buffer.getvalue()
    return best_image