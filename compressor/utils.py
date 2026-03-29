import fitz  # PyMuPDF
from PIL import Image
import io
import os


def compress_pdf(input_path, output_path, target_size_kb):
    """
    Compress a PDF to a target size in KB.
    Returns a dict with compression results.
    """
    original_size = os.path.getsize(input_path) / 1024

    # Get page count
    doc_temp = fitz.open(input_path)
    total_pages = len(doc_temp)
    doc_temp.close()

    result = {
        'original_size_kb': round(original_size, 1),
        'compressed_size_kb': None,
        'reduction_percent': None,
        'total_pages': total_pages,
        'success': False,
        'message': '',
    }

    # Already smaller than target
    if original_size <= target_size_kb:
        import shutil
        shutil.copy2(input_path, output_path)
        result['compressed_size_kb'] = round(original_size, 1)
        result['reduction_percent'] = 0
        result['success'] = True
        result['message'] = 'File is already smaller than target size.'
        return result

    # First try: just garbage collection + deflation (no image changes)
    try:
        doc = fitz.open(input_path)
        doc.save(output_path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
        doc.close()

        new_size = os.path.getsize(output_path) / 1024
        if new_size <= target_size_kb:
            result['compressed_size_kb'] = round(new_size, 1)
            result['reduction_percent'] = round(((original_size - new_size) / original_size) * 100, 1)
            result['success'] = True
            result['message'] = f'Compressed to {new_size:.1f} KB with optimization only.'
            return result
    except Exception:
        pass

    # Second try: reduce image quality step by step
    best_size = original_size

    for quality in range(80, 5, -5):
        try:
            doc = fitz.open(input_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                img_list = page.get_images(full=True)

                for img in img_list:
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        if not base_image:
                            continue

                        image = Image.open(io.BytesIO(base_image["image"]))

                        # Resize based on quality level
                        max_width = int(600 + (quality / 80) * 1400)
                        if image.width > max_width:
                            ratio = max_width / image.width
                            new_dim = (max_width, int(image.height * ratio))
                            image = image.resize(new_dim, Image.LANCZOS)

                        if image.mode != "RGB":
                            image = image.convert("RGB")

                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format="JPEG", quality=quality)
                        page.replace_image(xref, stream=img_buffer.getvalue())

                    except Exception:
                        continue

            doc.save(output_path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
            doc.close()

            new_size = os.path.getsize(output_path) / 1024
            best_size = new_size

            if new_size <= target_size_kb:
                result['compressed_size_kb'] = round(new_size, 1)
                result['reduction_percent'] = round(((original_size - new_size) / original_size) * 100, 1)
                result['success'] = True
                result['message'] = f'Successfully compressed to {new_size:.1f} KB (quality: {quality}%).'
                return result

        except Exception as e:
            result['message'] = f'Error during compression: {str(e)}'
            continue

    # Could not reach target but return best result
    result['compressed_size_kb'] = round(best_size, 1)
    result['reduction_percent'] = round(((original_size - best_size) / original_size) * 100, 1)
    result['success'] = True
    result['message'] = (
        f'Could not reach {target_size_kb} KB. '
        f'Best achieved: {best_size:.1f} KB ({result["reduction_percent"]}% reduction).'
    )
    return result
