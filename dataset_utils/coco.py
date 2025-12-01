from typing import List

LABELS = [
    "background",
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
    "tree-merged",
    "fence-merged",
    "ceiling-merged",
    "sky-other-merged",
    "cabinet-merged",
    "table-merged",
    "floor-other-merged",
    "pavement-merged",
    "mountain-merged",
    "grass-merged",
    "dirt-merged",
    "paper-merged",
    "food-other-merged",
    "building-other-merged",
    "rock-merged",
    "wall-other-merged",
    "rug-merged",
]


# according to panoptic_coco_categories.json in panopticapi/panoptic_coco_categories.json
LABEL_COLORS = [
    [0, 0, 0],
    [220, 20, 60],
    [119, 11, 32],
    [0, 0, 142],
    [0, 0, 230],
    [106, 0, 228],
    [0, 60, 100],
    [0, 80, 100],
    [0, 0, 70],
    [0, 0, 192],
    [250, 170, 30],
    [100, 170, 30],
    [0, 0, 0],  # id 12 color not assigned
    [220, 220, 0],
    [175, 116, 175],
    [250, 0, 30],
    [165, 42, 42],
    [255, 77, 255],
    [0, 226, 252],
    [182, 182, 255],
    [0, 82, 0],
    [120, 166, 157],
    [110, 76, 0],
    [174, 57, 255],
    [199, 100, 0],
    [72, 0, 118],
    [0, 0, 0],  # id 26 color not assigned
    [255, 179, 240],
    [0, 125, 92],
    [0, 0, 0],  # id 29 color not assigned
    [0, 0, 0],  # id 30 color not assigned
    [209, 0, 151],
    [188, 208, 182],
    [0, 220, 176],
    [255, 99, 164],
    [92, 0, 73],
    [133, 129, 255],
    [78, 180, 255],
    [0, 228, 0],
    [174, 255, 243],
    [45, 89, 255],
    [134, 134, 103],
    [145, 148, 174],
    [255, 208, 186],
    [197, 226, 255],
    [0, 0, 0],  # id 45 color not assigned
    [171, 134, 1],
    [109, 63, 54],
    [207, 138, 255],
    [151, 0, 95],
    [9, 80, 61],
    [84, 105, 51],
    [74, 65, 105],
    [166, 196, 102],
    [208, 195, 210],
    [255, 109, 65],
    [0, 143, 149],
    [179, 0, 194],
    [209, 99, 106],
    [5, 121, 0],
    [227, 255, 205],
    [147, 186, 208],
    [153, 69, 1],
    [3, 95, 161],
    [163, 255, 0],
    [119, 0, 170],
    [0, 0, 0],  # id 66 color not assigned
    [0, 182, 199],
    [0, 0, 0],  # id 68 color not assigned
    [0, 0, 0],  # id 69 color not assigned
    [0, 165, 120],
    [0, 0, 0],  # id 71 color not assigned
    [183, 130, 88],
    [95, 32, 0],
    [130, 114, 135],
    [110, 129, 133],
    [166, 74, 118],
    [219, 142, 185],
    [79, 210, 114],
    [178, 90, 62],
    [65, 70, 15],
    [127, 167, 115],
    [59, 105, 106],
    [0, 0, 0],  # id 83 color not assigned
    [142, 108, 45],
    [196, 172, 0],
    [95, 54, 80],
    [128, 76, 255],
    [201, 57, 1],
    [246, 0, 122],
    [191, 162, 208],
    [0, 0, 0],  # id 91 color not assigned
    [255, 255, 128],
    [147, 211, 203],
    [0, 0, 0],  # id 94 color not assigned
    [150, 100, 100],
    [0, 0, 0],  # id 96 color not assigned
    [0, 0, 0],  # id 97 color not assigned
    [0, 0, 0],  # id 98 color not assigned
    [0, 0, 0],  # id 99 color not assigned
    [168, 171, 172],
    [0, 0, 0],  # id 101 color not assigned
    [0, 0, 0],  # id 102 color not assigned
    [0, 0, 0],  # id 103 color not assigned
    [0, 0, 0],  # id 104 color not assigned
    [0, 0, 0],  # id 105 color not assigned
    [0, 0, 0],  # id 106 color not assigned
    [146, 112, 198],
    [0, 0, 0],  # id 108 color not assigned
    [210, 170, 100],
    [0, 0, 0],  # id 110 color not assigned
    [0, 0, 0],  # id 111 color not assigned
    [92, 136, 89],
    [0, 0, 0],  # id 113 color not assigned
    [0, 0, 0],  # id 114 color not assigned
    [0, 0, 0],  # id 115 color not assigned
    [0, 0, 0],  # id 116 color not assigned
    [0, 0, 0],  # id 117 color not assigned
    [218, 88, 184],
    [241, 129, 0],
    [0, 0, 0],  # id 120 color not assigned
    [0, 0, 0],  # id 121 color not assigned
    [217, 17, 255],
    [0, 0, 0],  # id 123 color not assigned
    [0, 0, 0],  # id 124 color not assigned
    [124, 74, 181],
    [0, 0, 0],  # id 126 color not assigned
    [0, 0, 0],  # id 127 color not assigned
    [70, 70, 70],
    [0, 0, 0],  # id 129 color not assigned
    [255, 228, 255],
    [0, 0, 0],  # id 131 color not assigned
    [0, 0, 0],  # id 132 color not assigned
    [154, 208, 0],
    [0, 0, 0],  # id 134 color not assigned
    [0, 0, 0],  # id 135 color not assigned
    [0, 0, 0],  # id 136 color not assigned
    [0, 0, 0],  # id 137 color not assigned
    [193, 0, 92],
    [0, 0, 0],  # id 139 color not assigned
    [0, 0, 0],  # id 140 color not assigned
    [76, 91, 113],
    [0, 0, 0],  # id 142 color not assigned
    [0, 0, 0],  # id 143 color not assigned
    [255, 180, 195],
    [106, 154, 176],
    [0, 0, 0],  # id 146 color not assigned
    [230, 150, 140],
    [60, 143, 255],
    [128, 64, 128],
    [0, 0, 0],  # id 150 color not assigned
    [92, 82, 55],
    [0, 0, 0],  # id 152 color not assigned
    [0, 0, 0],  # id 153 color not assigned
    [254, 212, 124],
    [73, 77, 174],
    [255, 160, 98],
    [0, 0, 0],  # id 157 color not assigned
    [0, 0, 0],  # id 158 color not assigned
    [255, 255, 255],
    [0, 0, 0],  # id 160 color not assigned
    [104, 84, 109],
    [0, 0, 0],  # id 162 color not assigned
    [0, 0, 0],  # id 163 color not assigned
    [0, 0, 0],  # id 164 color not assigned
    [0, 0, 0],  # id 165 color not assigned
    [169, 164, 131],
    [0, 0, 0],  # id 167 color not assigned
    [225, 199, 255],
    [0, 0, 0],  # id 169 color not assigned
    [0, 0, 0],  # id 170 color not assigned
    [137, 54, 74],
    [0, 0, 0],  # id 172 color not assigned
    [0, 0, 0],  # id 173 color not assigned
    [0, 0, 0],  # id 174 color not assigned
    [135, 158, 223],
    [7, 246, 231],
    [107, 255, 200],
    [58, 41, 149],
    [0, 0, 0],  # id 179 color not assigned
    [183, 121, 142],
    [255, 73, 97],
    [0, 0, 0],  # id 182 color not assigned
    [0, 0, 0],  # id 183 color not assigned
    [107, 142, 35],
    [190, 153, 153],
    [146, 139, 141],
    [70, 130, 180],
    [134, 199, 156],
    [209, 226, 140],
    [96, 36, 108],
    [96, 96, 96],
    [64, 170, 64],
    [152, 251, 152],
    [208, 229, 228],
    [206, 186, 171],
    [152, 161, 64],
    [116, 112, 0],
    [0, 114, 143],
    [102, 102, 156],
    [250, 141, 255],
]


PROMPT_TEMPLATE = """I want you to do semantic segmentation based on facial features. 

The label encodings are

```
{label_encodings}
```

Please draw a colorful mask, given the photo (the first image), the color palette and the label encodings. 
For your convenience, I've also give you a color palette (the rest of the images) for the label encodings.
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
