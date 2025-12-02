import os
from PIL import Image
import torch
import numpy as np
from typing import List, Literal
from pathlib import Path
from pydantic import validate_call
from pydantic import ConfigDict
from pixel_arena.dataset_utils.celeb_a_mask_hq import LABEL_COLORS as LABEL_COLORS_CELEB
from pixel_arena.dataset_utils.coco import LABEL_COLORS as LABEL_COLORS_COCO
from pixel_arena.dataset_utils.coco import (
    integer_mask_to_pil as integer_mask_to_pil_coco,
)
from pixel_arena.dataset_utils.celeb_a_mask_hq import (
    integer_mask_to_pil as integer_mask_to_pil_celeb,
)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def mask_raw_to_pmode(
    image: str | Path | Image.Image,
    dataset: Literal["celeb", "coco"],
    label_colors: List[List[int]] | None,
):
    # Load the image
    if isinstance(image, str | Path):
        assert os.path.exists(image), f"Image file {image} does not exist"
        mask_image = Image.open(image).convert("RGB")
    else:
        mask_image = image.convert("RGB")

    # Convert image to torch tensor
    # Shape: (H, W, 3)
    image_tensor = torch.from_numpy(np.array(mask_image)).float()
    H, W, C = image_tensor.shape

    # Convert label colors to tensor
    # Shape: (N, 3)
    if label_colors is None:
        if dataset == "celeb":
            label_colors = LABEL_COLORS_CELEB
        else:
            label_colors = LABEL_COLORS_COCO

    label_colors_tensor = torch.tensor(label_colors).float()

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
    if dataset == "celeb":
        reconstructed_mask = integer_mask_to_pil_celeb(integer_mask)
    else:
        reconstructed_mask = integer_mask_to_pil_coco(integer_mask)

    return reconstructed_mask
