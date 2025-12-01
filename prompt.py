from typing import List
from dataset_utils.celeb_a_mask_hq import LABEL_COLORS, LABELS

PROMPT_TEMPLATE = """I want you to do semantic segmentation based on facial features. 

The label encodings are

```
{label_encodings}
```

For you convenience, I've also give you a color palette (the second image) for the label encodings.

Please draw a colorful mask, given the photo (the first image), the color palette and the label encodings. 

Note that for the left and right used by the labels, these are with respect to the person in the image, NOT the image itself, so the left facial features of the person are on the right of the image. 
Check if you have labeled the features on the left of the image to be the right feature labels.
"""


def get_prompt(label_colors: List[List[int]] = None) -> str:
    if label_colors is None:
        label_colors = LABEL_COLORS

    string = []
    for label, color in zip(LABELS, label_colors):
        string.append(f"{label}: {color}")

    label_encodings = "\n".join(string)
    prompt = PROMPT_TEMPLATE.format(label_encodings=label_encodings)
    return prompt
