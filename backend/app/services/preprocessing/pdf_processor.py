import os
import fitz  # PyMuPDF
import logging
from typing import Dict, Any, List
from PIL import Image

logger = logging.getLogger(__name__)

def extract_pdf_pages_or_text(pdf_path: str, output_dir: str = "preprocessed", dpi: int = 300) -> Dict[str, Any]:
    """
    Renders all pages of a PDF document as high-resolution images using PyMuPDF (fitz)
    and extracts embedded vector text streams if present.
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    rendered_image_paths = []
    page_texts = []
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        logger.info(f"Processing PDF '{pdf_path}' ({total_pages} pages) at {dpi} DPI...")

        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for page_num in range(total_pages):
            page = doc[page_num]
            # Extract embedded vector text if available
            raw_page_text = page.get_text("text")
            if raw_page_text:
                page_texts.append(raw_page_text.strip())

            # Render page to high-res pixmap image
            pix = page.get_pixmap(matrix=mat, alpha=False)
            page_img_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.png")
            pix.save(page_img_path)
            rendered_image_paths.append(page_img_path)

        doc.close()

        combined_text = "\n\n--- Page Break ---\n\n".join(page_texts)

        return {
            "success": True,
            "total_pages": total_pages,
            "rendered_images": rendered_image_paths,
            "embedded_text": combined_text,
            "has_embedded_text": len(combined_text.strip()) > 20
        }
    except Exception as e:
        logger.error(f"PyMuPDF rendering error on {pdf_path}: {e}")
        # Fallback to single blank image if PDF is corrupted
        fallback_path = os.path.join(output_dir, f"{base_name}_fallback.png")
        img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
        img.save(fallback_path)
        return {
            "success": False,
            "error": str(e),
            "total_pages": 1,
            "rendered_images": [fallback_path],
            "embedded_text": "",
            "has_embedded_text": False
        }

process_pdf_document = extract_pdf_pages_or_text
