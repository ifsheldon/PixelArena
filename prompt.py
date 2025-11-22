PROMPT = """I want you to do semantic segmentation based on facial features. 

The label encodings are

```
[
    [0, 0, 0],  # 0 background
    [204, 0, 0],  # 1 skin
    [76, 153, 0],  # 2 nose
    [204, 204, 0],  # 3 eye_glass
    [51, 51, 255],  # 4 left_eye
    [204, 0, 204],  # 5 right_eye
    [0, 255, 255],  # 6 left_eyebrow
    [255, 204, 204],  # 7 right_eyebrow
    [102, 51, 0],  # 8 left_ear
    [255, 0, 0],  # 9 right_ear
    [102, 204, 0],  # 10 mouth
    [255, 255, 0],  # 11 upper_lip
    [0, 0, 153],  # 12 lower_lip
    [0, 0, 204],  # 13 hair
    [255, 51, 153],  # 14 hat
    [0, 204, 204],  # 15 ear_ring
    [0, 51, 0],  # 16 neck_lace
    [255, 153, 51],  # 17 neck
    [0, 204, 0],  # 18 cloth
]
```

For you convenience, I've also give you a color palette (the second image) for the label encodings.

Please draw a colorful mask, given the photo (the first image), the color palette and the label encodings. 

Note that for the left and right used by the labels, these are with respect to the person in the image, NOT the image itself, so the left facial features of the person are on the right of the image. 
Check if you have labeled the features on the left of the image to be the right feature labels.
"""
