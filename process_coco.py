"""
This script processes the COCO dataset by:
1. Selecting 150 random images from the dataset
2. Cropping the images to the shortest dimension
3. Upscaling the images to 1024x1024
4. Converting the masks to P-mode
5. Storing the processed files in the destination directories
"""

import random
import shutil
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from pixel_arena.dataset_utils.coco import integer_mask_to_pil


def process_pipeline():
    # Set random seed
    random.seed(77)

    # Define paths
    base_dir = Path("coco-dataset")

    # Source directories
    img_src_dir = base_dir / "val2017"
    mask_src_dir = base_dir / "semantic_segmentation_val2017"
    if not mask_src_dir.exists():
        raise FileNotFoundError(
            "Could not find semantic segmentation directory (checked 'semantic_segmentation_val2017')"
        )

    print(f"Using mask source directory: {mask_src_dir}")

    dst_dir = Path("eval-set/coco")

    # Destination directories
    img_dst_dir = dst_dir / "images-150"
    mask_dst_dir = dst_dir / "masks-1024"

    # Clean up and recreate destination directories if they exist (user said they deleted old results, but good to be safe/consistent)
    if img_dst_dir.exists():
        shutil.rmtree(img_dst_dir)
    img_dst_dir.mkdir(exist_ok=True, parents=True)

    if mask_dst_dir.exists():
        shutil.rmtree(mask_dst_dir)
    mask_dst_dir.mkdir(exist_ok=True, parents=True)

    # Get all image files
    all_images = sorted(list(img_src_dir.glob("*.jpg")))
    print(f"Found {len(all_images)} images in {img_src_dir}")

    # Select 150 random images
    if len(all_images) < 150:
        print("Warning: Less than 150 images found. Selecting all.")
        selected_images = all_images
    else:
        selected_images = random.sample(all_images, 150)

    print(f"Selected {len(selected_images)} images.")

    success_count = 0
    target_size = (1024, 1024)

    for img_path in tqdm(selected_images, desc="Processing"):
        try:
            file_stem = img_path.stem
            mask_path = mask_src_dir / f"{file_stem}.png"

            if not mask_path.exists():
                print(f"Warning: Mask not found for {img_path.name}")
                continue

            with Image.open(img_path) as img, Image.open(mask_path) as mask:
                # 1. Center-crop with shortest dimension
                w, h = img.size
                min_dim = min(w, h)

                left = (w - min_dim) // 2
                top = (h - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim

                crop_box = (left, top, right, bottom)

                img_cropped = img.crop(crop_box)
                mask_cropped = mask.crop(crop_box)

                # 2. Upscale to 1024x1024 using nearest neighbor
                img_resized = img_cropped.resize(target_size, resample=Image.NEAREST)
                mask_resized = mask_cropped.resize(target_size, resample=Image.NEAREST)

                # 3. Convert mask to P-mode
                # Convert to numpy array first
                mask_np = np.array(mask_resized)
                # Convert to torch tensor (integers)
                mask_tensor = torch.from_numpy(mask_np).to(torch.uint8)
                # Use dataset_utils function to convert to P-mode
                mask_pmode = integer_mask_to_pil(mask_tensor)

                # 4. Store processed files
                img_resized.save(img_dst_dir / img_path.name)
                mask_pmode.save(mask_dst_dir / mask_path.name)

                success_count += 1

        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")
            import traceback

            traceback.print_exc()

    print(f"Successfully processed {success_count} image-mask pairs.")


if __name__ == "__main__":
    process_pipeline()
