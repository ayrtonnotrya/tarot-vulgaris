
import os
from PIL import Image

PROJECT_ROOT = "/home/ayrtondouglas/Projetos/tarot-vulgaris"
FRAME_PATH = os.path.join(PROJECT_ROOT, "assets/moldura.png")
INPUT_DIR = os.path.join(PROJECT_ROOT, "assets/raw")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets/final")

def remove_green_background(image):
    """
    Removes green background using standard chroma key logic with pure PIL.
    """
    img = image.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    
    for item in datas:
        # item is (R, G, B, A)
        r, g, b, a = item
        
        # Simple Green Screen Heuristic
        # G is dominant and brighter than R and B
        if g > 100 and g > (r + 40) and g > (b + 40):
            # Transparent
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)
    
    img.putdata(newData)
    return img

def process_images():
    if not os.path.exists(FRAME_PATH):
        print(f"Error: Frame not found at {FRAME_PATH}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    print("Loading frame...")
    frame_orig = Image.open(FRAME_PATH)
    frame = remove_green_background(frame_orig)
    print("Frame processed (background removed).")

    # Get list of images
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".png")]
    total = len(files)
    
    print(f"Found {total} images in {INPUT_DIR}")

    for i, filename in enumerate(sorted(files)):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            # Open source image
            img = Image.open(input_path).convert("RGBA")
            
            # Resize frame to match image if necessary
            if frame.size != img.size:
               frame_current = frame.resize(img.size, Image.Resampling.LANCZOS)
            else:
               frame_current = frame

            # Composition: Frame OVER Image
            # Create a new blank image with the same size
            combined = Image.new('RGBA', img.size)
            # Paste background (card image)
            combined.paste(img, (0, 0))
            # Paste foreground (frame) with alpha mask
            combined.paste(frame_current, (0, 0), mask=frame_current)
            
            # Save
            combined.save(output_path, "PNG")
            print(f"[{i+1}/{total}] Processed {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("Processing complete!")

if __name__ == "__main__":
    process_images()
