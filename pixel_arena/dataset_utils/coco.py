from typing import List
import torch
from PIL import Image

LABELS = [
    "other",
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    None,
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    None,
    "backpack",
    "umbrella",
    None,
    None,
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    None,
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    None,
    "dining table",
    None,
    None,
    "toilet",
    None,
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    None,
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
    None,
    "banner",
    "blanket",
    None,
    "bridge",
    None,
    None,
    None,
    None,
    "cardboard",
    None,
    None,
    None,
    None,
    None,
    None,
    "counter",
    None,
    "curtain",
    None,
    None,
    "door-stuff",
    None,
    None,
    None,
    None,
    None,
    "floor-wood",
    "flower",
    None,
    None,
    "fruit",
    None,
    None,
    "gravel",
    None,
    None,
    "house",
    None,
    "light",
    None,
    None,
    "mirror-stuff",
    None,
    None,
    None,
    None,
    "net",
    None,
    None,
    "pillow",
    None,
    None,
    "platform",
    "playingfield",
    None,
    "railroad",
    "river",
    "road",
    None,
    "roof",
    None,
    None,
    "sand",
    "sea",
    "shelf",
    None,
    None,
    "snow",
    None,
    "stairs",
    None,
    None,
    None,
    None,
    "tent",
    None,
    "towel",
    None,
    None,
    "wall-brick",
    None,
    None,
    None,
    "wall-stone",
    "wall-tile",
    "wall-wood",
    "water-other",
    None,
    "window-blind",
    "window-other",
    None,
    None,
    "tree",
    "fence",
    "ceiling",
    "sky-other",
    "cabinet",
    "table",
    "floor-other",
    "pavement",
    "mountain",
    "grass",
    "dirt",
    "paper",
    "food-other",
    "building-other",
    "rock",
    "wall-other",
    "rug",
]


# according to panoptic_coco_categories.json in panopticapi/panoptic_coco_categories.json
LABEL_COLORS = [
    [0, 0, 0],  # id 0: other
    [220, 20, 60],  # id 1: person
    [119, 11, 32],  # id 2: bicycle
    [0, 0, 142],  # id 3: car
    [0, 0, 230],  # id 4: motorcycle
    [106, 0, 228],  # id 5: airplane
    [0, 60, 100],  # id 6: bus
    [0, 80, 100],  # id 7: train
    [0, 0, 70],  # id 8: truck
    [0, 0, 192],  # id 9: boat
    [250, 170, 30],  # id 10: traffic light
    [100, 170, 30],  # id 11: fire hydrant
    [0, 0, 0],  # id 12 color not assigned
    [220, 220, 0],  # id 13: stop sign
    [175, 116, 175],  # id 14: parking meter
    [250, 0, 30],  # id 15: bench
    [165, 42, 42],  # id 16: bird
    [255, 77, 255],  # id 17: cat
    [0, 226, 252],  # id 18: dog
    [182, 182, 255],  # id 19: horse
    [0, 82, 0],  # id 20: sheep
    [120, 166, 157],  # id 21: cow
    [110, 76, 0],  # id 22: elephant
    [174, 57, 255],  # id 23: bear
    [199, 100, 0],  # id 24: zebra
    [72, 0, 118],  # id 25: giraffe
    [0, 0, 0],  # id 26 color not assigned
    [255, 179, 240],  # id 27: backpack
    [0, 125, 92],  # id 28: umbrella
    [0, 0, 0],  # id 29 color not assigned
    [0, 0, 0],  # id 30 color not assigned
    [209, 0, 151],  # id 31: handbag
    [188, 208, 182],  # id 32: tie
    [0, 220, 176],  # id 33: suitcase
    [255, 99, 164],  # id 34: frisbee
    [92, 0, 73],  # id 35: skis
    [133, 129, 255],  # id 36: snowboard
    [78, 180, 255],  # id 37: sports ball
    [0, 228, 0],  # id 38: kite
    [174, 255, 243],  # id 39: baseball bat
    [45, 89, 255],  # id 40: baseball glove
    [134, 134, 103],  # id 41: skateboard
    [145, 148, 174],  # id 42: surfboard
    [255, 208, 186],  # id 43: tennis racket
    [197, 226, 255],  # id 44: bottle
    [0, 0, 0],  # id 45 color not assigned
    [171, 134, 1],  # id 46: wine glass
    [109, 63, 54],  # id 47: cup
    [207, 138, 255],  # id 48: fork
    [151, 0, 95],  # id 49: knife
    [9, 80, 61],  # id 50: spoon
    [84, 105, 51],  # id 51: bowl
    [74, 65, 105],  # id 52: banana
    [166, 196, 102],  # id 53: apple
    [208, 195, 210],  # id 54: sandwich
    [255, 109, 65],  # id 55: orange
    [0, 143, 149],  # id 56: broccoli
    [179, 0, 194],  # id 57: carrot
    [209, 99, 106],  # id 58: hot dog
    [5, 121, 0],  # id 59: pizza
    [227, 255, 205],  # id 60: donut
    [147, 186, 208],  # id 61: cake
    [153, 69, 1],  # id 62: chair
    [3, 95, 161],  # id 63: couch
    [163, 255, 0],  # id 64: potted plant
    [119, 0, 170],  # id 65: bed
    [0, 0, 0],  # id 66 color not assigned
    [0, 182, 199],  # id 67: dining table
    [0, 0, 0],  # id 68 color not assigned
    [0, 0, 0],  # id 69 color not assigned
    [0, 165, 120],  # id 70: toilet
    [0, 0, 0],  # id 71 color not assigned
    [183, 130, 88],  # id 72: tv
    [95, 32, 0],  # id 73: laptop
    [130, 114, 135],  # id 74: mouse
    [110, 129, 133],  # id 75: remote
    [166, 74, 118],  # id 76: keyboard
    [219, 142, 185],  # id 77: cell phone
    [79, 210, 114],  # id 78: microwave
    [178, 90, 62],  # id 79: oven
    [65, 70, 15],  # id 80: toaster
    [127, 167, 115],  # id 81: sink
    [59, 105, 106],  # id 82: refrigerator
    [0, 0, 0],  # id 83 color not assigned
    [142, 108, 45],  # id 84: book
    [196, 172, 0],  # id 85: clock
    [95, 54, 80],  # id 86: vase
    [128, 76, 255],  # id 87: scissors
    [201, 57, 1],  # id 88: teddy bear
    [246, 0, 122],  # id 89: hair drier
    [191, 162, 208],  # id 90: toothbrush
    [0, 0, 0],  # id 91 color not assigned
    [255, 255, 128],  # id 92: banner
    [147, 211, 203],  # id 93: blanket
    [0, 0, 0],  # id 94 color not assigned
    [150, 100, 100],  # id 95: bridge
    [0, 0, 0],  # id 96 color not assigned
    [0, 0, 0],  # id 97 color not assigned
    [0, 0, 0],  # id 98 color not assigned
    [0, 0, 0],  # id 99 color not assigned
    [168, 171, 172],  # id 100: cardboard
    [0, 0, 0],  # id 101 color not assigned
    [0, 0, 0],  # id 102 color not assigned
    [0, 0, 0],  # id 103 color not assigned
    [0, 0, 0],  # id 104 color not assigned
    [0, 0, 0],  # id 105 color not assigned
    [0, 0, 0],  # id 106 color not assigned
    [146, 112, 198],  # id 107: counter
    [0, 0, 0],  # id 108 color not assigned
    [210, 170, 100],  # id 109: curtain
    [0, 0, 0],  # id 110 color not assigned
    [0, 0, 0],  # id 111 color not assigned
    [92, 136, 89],  # id 112: door-stuff
    [0, 0, 0],  # id 113 color not assigned
    [0, 0, 0],  # id 114 color not assigned
    [0, 0, 0],  # id 115 color not assigned
    [0, 0, 0],  # id 116 color not assigned
    [0, 0, 0],  # id 117 color not assigned
    [218, 88, 184],  # id 118: floor-wood
    [241, 129, 0],  # id 119: flower
    [0, 0, 0],  # id 120 color not assigned
    [0, 0, 0],  # id 121 color not assigned
    [217, 17, 255],  # id 122: fruit
    [0, 0, 0],  # id 123 color not assigned
    [0, 0, 0],  # id 124 color not assigned
    [124, 74, 181],  # id 125: gravel
    [0, 0, 0],  # id 126 color not assigned
    [0, 0, 0],  # id 127 color not assigned
    [70, 70, 70],  # id 128: house
    [0, 0, 0],  # id 129 color not assigned
    [255, 228, 255],  # id 130: light
    [0, 0, 0],  # id 131 color not assigned
    [0, 0, 0],  # id 132 color not assigned
    [154, 208, 0],  # id 133: mirror-stuff
    [0, 0, 0],  # id 134 color not assigned
    [0, 0, 0],  # id 135 color not assigned
    [0, 0, 0],  # id 136 color not assigned
    [0, 0, 0],  # id 137 color not assigned
    [193, 0, 92],  # id 138: net
    [0, 0, 0],  # id 139 color not assigned
    [0, 0, 0],  # id 140 color not assigned
    [76, 91, 113],  # id 141: pillow
    [0, 0, 0],  # id 142 color not assigned
    [0, 0, 0],  # id 143 color not assigned
    [255, 180, 195],  # id 144: platform
    [106, 154, 176],  # id 145: playingfield
    [0, 0, 0],  # id 146 color not assigned
    [230, 150, 140],  # id 147: railroad
    [60, 143, 255],  # id 148: river
    [128, 64, 128],  # id 149: road
    [0, 0, 0],  # id 150 color not assigned
    [92, 82, 55],  # id 151: roof
    [0, 0, 0],  # id 152 color not assigned
    [0, 0, 0],  # id 153 color not assigned
    [254, 212, 124],  # id 154: sand
    [73, 77, 174],  # id 155: sea
    [255, 160, 98],  # id 156: shelf
    [0, 0, 0],  # id 157 color not assigned
    [0, 0, 0],  # id 158 color not assigned
    [255, 255, 255],  # id 159: snow
    [0, 0, 0],  # id 160 color not assigned
    [104, 84, 109],  # id 161: stairs
    [0, 0, 0],  # id 162 color not assigned
    [0, 0, 0],  # id 163 color not assigned
    [0, 0, 0],  # id 164 color not assigned
    [0, 0, 0],  # id 165 color not assigned
    [169, 164, 131],  # id 166: tent
    [0, 0, 0],  # id 167 color not assigned
    [225, 199, 255],  # id 168: towel
    [0, 0, 0],  # id 169 color not assigned
    [0, 0, 0],  # id 170 color not assigned
    [137, 54, 74],  # id 171: wall-brick
    [0, 0, 0],  # id 172 color not assigned
    [0, 0, 0],  # id 173 color not assigned
    [0, 0, 0],  # id 174 color not assigned
    [135, 158, 223],  # id 175: wall-stone
    [7, 246, 231],  # id 176: wall-tile
    [107, 255, 200],  # id 177: wall-wood
    [58, 41, 149],  # id 178: water-other
    [0, 0, 0],  # id 179 color not assigned
    [183, 121, 142],  # id 180: window-blind
    [255, 73, 97],  # id 181: window-other
    [0, 0, 0],  # id 182 color not assigned
    [0, 0, 0],  # id 183 color not assigned
    [107, 142, 35],  # id 184: tree
    [190, 153, 153],  # id 185: fence
    [146, 139, 141],  # id 186: ceiling
    [70, 130, 180],  # id 187: sky-other
    [134, 199, 156],  # id 188: cabinet
    [209, 226, 140],  # id 189: table
    [96, 36, 108],  # id 190: floor-other
    [96, 96, 96],  # id 191: pavement
    [64, 170, 64],  # id 192: mountain
    [152, 251, 152],  # id 193: grass
    [208, 229, 228],  # id 194: dirt
    [206, 186, 171],  # id 195: paper
    [152, 161, 64],  # id 196: food-other
    [116, 112, 0],  # id 197: building-other
    [0, 114, 143],  # id 198: rock
    [102, 102, 156],  # id 199: wall-other
    [250, 141, 255],  # id 200: rug
]

LABEL_COLOR_TENSOR = torch.tensor(LABEL_COLORS, dtype=torch.uint8)


PROMPT_TEMPLATE = """I want you to do semantic segmentation based on the given category labels.

The label encodings are

```
{label_encodings}
```

Please draw a colorful mask, given the photo (the first image), the color palette and the label encodings. 
For your convenience, I've also give you a color palette (the rest of the images) for the label encodings.

You can first recognize all categories of all subjects in the first image and then draw the mask. Note that the first category `other` is used only when there're no related category labels for a subject in the image.
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
        if label is None:
            continue
        string.append(f"{label}: {color}")

    label_encodings = "\n".join(string)
    prompt = PROMPT_TEMPLATE.format(label_encodings=label_encodings)
    return prompt


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
    assert mask.max() <= 200, "Mask should be <= 200"
    mask_np = mask.numpy().astype("uint8")
    mask_pil = Image.fromarray(mask_np, mode="P")
    flat_palette = LABEL_COLOR_TENSOR.flatten().tolist()
    flat_palette += [0] * (768 - len(flat_palette))
    mask_pil.putpalette(flat_palette)
    return mask_pil
