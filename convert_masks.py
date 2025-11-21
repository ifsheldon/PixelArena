import os
import glob
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from celeb_a_mask_hq import LABEL_COLORS, integer_mask_to_pil


def process_image(image_path):
    # Load the image
    mask_image = Image.open(image_path).convert("RGB")

    # Convert image to torch tensor
    # Shape: (H, W, 3)
    image_tensor = torch.from_numpy(np.array(mask_image)).float()
    H, W, C = image_tensor.shape

    # Convert label colors to tensor
    # Shape: (N, 3)
    label_colors_tensor = torch.tensor(LABEL_COLORS).float()

    # Flatten image to (H*W, 3) for distance calculation
    flat_image = image_tensor.reshape(-1, 3)

    # Calculate Euclidean distance between each pixel and each label color
    # flat_image: (H*W, 3)
    # label_colors_tensor: (N, 3)
    # dists result: (H*W, N)
    # Using cdist is efficient for this pairwise distance calculation
    dists = torch.cdist(flat_image, label_colors_tensor)

    # Find the index of the minimum distance for each pixel (the nearest label)
    nearest_label_indices = torch.argmin(dists, dim=1)

    # Reshape back to (H, W) to get the integer mask
    integer_mask = nearest_label_indices.reshape(H, W).to(torch.uint8)

    # Convert back to PIL P-mode image
    reconstructed_mask = integer_mask_to_pil(integer_mask)

    return reconstructed_mask


def main():
    # Search for files matching the pattern in ./test
    # Pattern: *.mask.[0, 1, 2].raw.jpg
    # We can use glob with a character set for [0-2]
    search_pattern = os.path.join("./test", "*.mask.[0-2].raw.jpg")
    files = glob.glob(search_pattern)

    print(f"Found {len(files)} files to process.")

    for file_path in tqdm(files):
        try:
            # Construct output path
            # Replace .raw.jpg with .pred.png
            output_path = file_path.replace(".raw.jpg", ".pred.png")

            # Process
            result_image = process_image(file_path)

            # Save
            result_image.save(output_path)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()
