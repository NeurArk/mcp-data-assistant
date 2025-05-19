#!/usr/bin/env python3
"""
Convert PDF files to images for visualization.
Requires: pip install pdf2image pillow
"""

import os
import sys
from pathlib import Path
import argparse
from pdf2image import convert_from_path
from PIL import Image

def pdf_to_images(pdf_path, output_dir=None, dpi=150):
    """Convert a PDF file to images (one per page)."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    # Create output directory
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"Converting {pdf_path} to images...")
    
    # Convert PDF to list of PIL Image objects
    images = convert_from_path(pdf_path, dpi=dpi)
    
    # Save each page as an image
    for i, image in enumerate(images):
        image_path = output_dir / f"page_{i+1:02d}.png"
        image.save(image_path, "PNG")
        print(f"Saved: {image_path}")
    
    print(f"Conversion complete. {len(images)} page(s) saved to {output_dir}")
    return output_dir

def create_combined_image(output_dir):
    """Combine all page images into a single vertical image."""
    output_dir = Path(output_dir)
    image_files = sorted(output_dir.glob("page_*.png"))
    
    if not image_files:
        print("No images found to combine")
        return
    
    # Load all images
    images = [Image.open(img) for img in image_files]
    
    # Calculate total height
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    
    # Create new combined image
    combined = Image.new('RGB', (total_width, total_height), color='white')
    
    # Paste images vertically
    y_offset = 0
    for img in images:
        # Center horizontally
        x_offset = (total_width - img.width) // 2
        combined.paste(img, (x_offset, y_offset))
        y_offset += img.height
    
    # Save combined image
    combined_path = output_dir / "combined_full_document.png"
    combined.save(combined_path)
    print(f"Created combined image: {combined_path}")
    
    # Also create a smaller version for easier viewing
    thumb_width = 800
    thumb_height = int(total_height * (thumb_width / total_width))
    thumbnail = combined.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    thumb_path = output_dir / "combined_thumbnail.png"
    thumbnail.save(thumb_path)
    print(f"Created thumbnail: {thumb_path}")
    
    return combined_path

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to images")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--output-dir", help="Output directory for images")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for conversion (default: 150)")
    parser.add_argument("--combine", action="store_true", help="Create a combined image of all pages")
    
    args = parser.parse_args()
    
    # Convert PDF to images
    output_dir = pdf_to_images(args.pdf_path, args.output_dir, args.dpi)
    
    # Optionally create combined image
    if args.combine and output_dir:
        create_combined_image(output_dir)

if __name__ == "__main__":
    main()