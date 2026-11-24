
# Pixora

**Less weight. More room for creativity.**

Pixora is a Python-based image compression application built with Streamlit. It offers two different image compression approaches: Principal Component Analysis (PCA) and Smart Image Compression.

## Features

### PCA Compressor
- Image reconstruction using Principal Component Analysis concepts.
- Randomized Singular Value Decomposition.
- Adjustable quality retention.
- MSE and PSNR quality metrics.
- Original image dimensions preserved.
- WebP output.

### Smart Compressor
- Target file-size compression.
- Supports JPEG and WebP output.
- Binary search for encoding quality.
- Target size restricted to the original uploaded file size.
- Original image dimensions preserved.

### Interface
- Drag-and-drop image upload.
- Original and compressed image previews.
- Original size and new size comparison.
- Actual file-size reduction percentage.
- Light and dark themes.
- Download compressed images.

## Technologies Used

- Python
- Streamlit
- NumPy
- Pillow
- Randomized SVD
- Principal Component Analysis

## Project Structure

```text
Pixora/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── pca_compress.py
├── smart_compress.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Pixora.git
cd Pixora
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Pixora:

```bash
streamlit run app.py
```

## How It Works

### PCA Compression

PCA reduces the number of principal components used to reconstruct image colour-channel matrices.

The reconstructed image retains its original pixel dimensions, but some visual information may be lost.

MSE and PSNR are used to evaluate reconstruction quality before final WebP encoding.

### Smart Compression

Smart Compression uses JPEG or WebP encoding quality adjustments.

A binary search finds the highest quality that can fit within the requested file size, when possible.

The target size cannot exceed the original uploaded file size.

## Important Notes

- Neither compression method guarantees a smaller output for every image.
- PCA quality retention is not the same as file-size reduction.
- Smart Compression may not reach extremely small target sizes.
- Both methods preserve image width and height, but image encoding can change visual quality.
- PCA is computationally more expensive than ordinary image encoding.

## License

MIT License
