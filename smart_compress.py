from PIL import Image, ImageOps
from io import BytesIO
def encode_image(image, output_format, quality):
    buffer = BytesIO()
    if output_format == "JPEG":
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=False
        )
    else:
        image.save(
            buffer,
            format="WEBP",
            quality=quality,
            method=2
        )
    return buffer.getvalue()
def smart_compress(image, target_kb, output_format="WEBP"):
    image = ImageOps.exif_transpose(image).convert("RGB")
    target_bytes = int(target_kb * 1024)
    low = 10
    high = 95
    best_data = None
    best_quality = 10
    smallest_data = None
    smallest_quality = 10
    smallest_size = float("inf")
    while low <= high:
        quality = (low + high) // 2
        compressed_data = encode_image(
            image,
            output_format,
            quality
        )
        compressed_size = len(compressed_data)
        if compressed_size < smallest_size:
            smallest_size = compressed_size
            smallest_data = compressed_data
            smallest_quality = quality
        if compressed_size <= target_bytes:
            best_data = compressed_data
            best_quality = quality
            low = quality + 1
        else:
            high = quality - 1
    target_achieved = best_data is not None
    if target_achieved:
        final_data = best_data
        final_quality = best_quality
    else:
        final_data = smallest_data
        final_quality = smallest_quality
    preview = Image.open(
        BytesIO(final_data)
    ).copy()
    return (
        final_data,
        preview,
        final_quality,
        target_achieved
    )