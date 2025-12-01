"""
This file contains the labels and color palette for the Celeb-A dataset.
"""

import torch
from PIL import Image
from typing import List

LABELS = [
    "background",  # 0
    "skin",  # 1
    "nose",  # 2
    "eye_glass",  # 3
    "left_eye",  # 4, left eye
    "right_eye",  # 5, right eye
    "left_eyebrow",  # 6, left eyebrow
    "right_eyebrow",  # 7, right eyebrow
    "left_ear",  # 8, left ear
    "right_ear",  # 9, right ear
    "mouth",  # 10
    "upper_lip",  # 11, upper lip
    "lower_lip",  # 12, lower lip
    "hair",  # 13
    "hat",  # 14
    "ear_ring",  # 15, ear ring
    "necklace",  # 16, necklace
    "neck",  # 17
    "cloth",  # 18
]

NUM_CLASSES = len(LABELS)

LABEL_COLORS = [
    [0, 0, 0],  # 0 background
    [204, 0, 0],  # 1 skin
    [76, 153, 0],  # 2 nose
    [204, 204, 0],  # 3 eye_glass
    [51, 51, 255],  # 4 l_eye
    [204, 0, 204],  # 5 right_eye
    [0, 255, 255],  # 6 left_eyebrow
    [255, 204, 204],  # 7 right_eyebrow
    [102, 51, 0],  # 8 left_ear
    [255, 0, 0],  # 9 right_ear
    [102, 204, 0],  # 10 mouth
    [255, 255, 0],  # 11 u_lip
    [0, 0, 153],  # 12 lower_lip
    [0, 0, 204],  # 13 hair
    [255, 51, 153],  # 14 hat
    [0, 204, 204],  # 15 ear_ring
    [0, 51, 0],  # 16 necklace
    [255, 153, 51],  # 17 neck
    [0, 204, 0],  # 18 cloth
]

LABEL_COLOR_TENSOR = torch.tensor(LABEL_COLORS, dtype=torch.uint8)
LABEL_TO_INDEX = {label: i for i, label in enumerate(LABELS)}


def integer_mask_to_pil(mask: torch.Tensor) -> Image.Image:
    """
    Turn a mask tensor into a PIL image.

    Args:
        mask: Mask tensor.

    Returns:
        PIL image.
    """
    assert mask.ndim == 2 or mask.ndim == 3, (
        f"Mask should be (H, W) or (1, H, W), got {mask.shape}"
    )
    if mask.ndim == 3:
        assert mask.shape[0] == 1, (
            f"Mask should be (1, H, W) or (H, W), got {mask.shape}"
        )
        mask = mask.squeeze(0)

    assert not (
        torch.is_floating_point(mask)
        or torch.is_complex(mask)
        or mask.dtype == torch.bool
    ), "Mask should be integers"
    assert mask.max() <= 18, "Mask should be <= 18"
    mask_np = mask.numpy().astype("uint8")
    mask_pil = Image.fromarray(mask_np, mode="P")
    flat_palette = LABEL_COLOR_TENSOR.flatten().tolist()
    flat_palette += [0] * (768 - len(flat_palette))
    mask_pil.putpalette(flat_palette)
    return mask_pil


PROMPT_TEMPLATE = """I want you to do semantic segmentation based on facial features. 

The label encodings are

```
{label_encodings}
```

For your convenience, I've also give you a color palette (the second image) for the label encodings.

Please draw a colorful mask, given the photo (the first image), the color palette and the label encodings. 

Note that for the left and right used by the labels, these are with respect to the person in the image, NOT the image itself, so the left facial features of the person are on the right of the image. 
Check if you have labeled the features on the left of the image to be the right feature labels.
"""


def get_prompt(label_colors: List[List[int]] = None) -> str:
    if label_colors is None:
        label_colors = LABEL_COLORS
    else:
        assert len(label_colors) == len(LABELS), (
            f"Length of label colors ({len(label_colors)}) should be equal to the number of labels ({len(LABELS)})"
        )

    string = []
    for label, color in zip(LABELS, label_colors):
        string.append(f"{label}: {color}")

    label_encodings = "\n".join(string)
    prompt = PROMPT_TEMPLATE.format(label_encodings=label_encodings)
    return prompt
