import os
from PIL import Image
import sys

# Constants
# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

INPUT_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'assets', 'optimized')

def compress_images():
    # Check if PIL is installed
    try:
        import PIL
    except ImportError:
        print("Error: Pillow library is not installed. Please run 'pip install Pillow' first.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_files = len(files)
    
    print(f"Found {total_files} images to compress...")
    
    saved_bytes = 0
    original_total_bytes = 0
    
    for i, filename in enumerate(files):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with Image.open(input_path) as img:
                original_size = os.path.getsize(input_path)
                original_total_bytes += original_size
                
                # Convert to RGB if necessary (e.g. if RGBA) to avoid issues with some formats, 
                # but for PNG transparency we might want to keep RGBA or convert to P with transparency.
                # Since these are likely generated art, let's try to preserve transparency if it exists,
                # otherwise just quantize.
                
                # Method: Quantize to 256 colors (8-bit)
                # This drastically reduces size for illustrations without changing resolution.
                # dither=Image.FLOYDSTEINBERG is default and usually good for gradients.
                if img.mode != 'P':
                    # verify if it has transparency
                    if img.mode == 'RGBA':
                         # quantize with alpha
                         optimized_img = img.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
                    else:
                         optimized_img = img.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
                else:
                    optimized_img = img

                # Save with optimization
                optimized_img.save(output_path, "PNG", optimize=True)
                
                new_size = os.path.getsize(output_path)
                saved = original_size - new_size
                saved_bytes += saved
                
                percent = (saved / original_size) * 100
                print(f"[{i+1}/{total_files}] {filename}: {original_size/1024/1024:.2f}MB -> {new_size/1024/1024:.2f}MB (-{percent:.1f}%)")

        except Exception as e:
            print(f"[ERROR] Could not compress {filename}: {e}")

    print("-" * 30)
    print(f"Compression Complete!")
    print(f"Total Original Size: {original_total_bytes/1024/1024:.2f} MB")
    print(f"Total Saved: {saved_bytes/1024/1024:.2f} MB")
    if original_total_bytes > 0:
        total_percent = (saved_bytes / original_total_bytes) * 100
        print(f"Overall Reduction: {total_percent:.1f}%")
    print(f"Optimized images are in: {OUTPUT_DIR}")
    print("-" * 30)

if __name__ == "__main__":
    compress_images()
