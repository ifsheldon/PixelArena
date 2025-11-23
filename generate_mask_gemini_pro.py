"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google import genai
from google.genai import types
from google.genai.client import AsyncClient
from pathlib import Path
from PIL import Image
import asyncio
from tqdm.asyncio import tqdm_asyncio
import random
import logging
from prompt import get_prompt
from asynciolimiter import Limiter
from typing import List

# parameters when it's run in CLI
MODEL = "gemini-3-pro-image-preview"
IMAGE_DIR = Path("./eval-set/images-150")
OUTPUT_DIR = Path("test-shuffle")
CLIENT_IDX = None
COLOR_PALETTE_PATH = Path("seg-labels.png")
ATTEMPTS = 3
# end of parameters

CLIENTS = [
    # LF 0
    genai.Client(
        api_key="AIzaSyD00P48lTw9vZy2wEVGxxbsWJRJrTUVr3o",
    ).aio,
    # LF 1
    genai.Client(
        api_key="AIzaSyC54rwWvN69P0scm1vEd4YRzk7smrPWzJs",
    ).aio,
    # Sizhe
    genai.Client(
        api_key="AIzaSyCqVg3CbqjJS1CERlnuz0pI36Y1JPEBEtI",
    ).aio,
]

RPM = 12  # tier 1 -> RPM = 20 with a bit buffer
LIMITERS = [Limiter(RPM / 60) for _ in range(len(CLIENTS))]

logger = logging.getLogger("generate_mask_gemini")
logging.basicConfig(level=logging.WARNING)


async def get_client(idx=None) -> AsyncClient:
    if idx is None:
        idx = random.randint(0, len(CLIENTS) - 1)
    else:
        assert 0 <= idx < len(CLIENTS)

    limiter = LIMITERS[idx]
    await limiter.wait()
    return CLIENTS[idx]


async def gen_mask(
    original_image_path: Path,
    color_palette_path: Path,
    output_dir: Path,
    attempts: int,
    label_colors: List[List[int]] | None,
    client_idx: int | None,
):
    contents = [
        # first image is the original image
        Image.open(original_image_path).convert("RGB"),
        # second image is the color palette, as mentioned in the prompt
        Image.open(color_palette_path).convert("RGB"),
        get_prompt(label_colors),
    ]

    original_file_name = original_image_path.stem

    thinking_config = (
        types.ThinkingConfig(include_thoughts=True)
        if MODEL == "gemini-3-pro-image-preview"
        else None
    )
    image_size = "1K" if MODEL == "gemini-3-pro-image-preview" else None

    for attempt_idx in range(attempts):
        client = await get_client(client_idx)

        try:
            response = await client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    response_modalities=[
                        "IMAGE",
                        "TEXT",
                    ],
                    image_config=types.ImageConfig(
                        aspect_ratio="1:1",
                        image_size=image_size,
                    ),
                    top_p=0.95,
                    thinking_config=thinking_config,
                ),
            )

            if response.parts is None:
                logger.warning(f"Generation for {original_file_name} failed")
                break

            for part in response.parts:
                # if part.thought:
                #     if part.text:
                #         print(part.text)
                #     elif image := part.as_image():
                #         image.show()
                if part.text is not None:
                    # print(part.text)
                    pass
                elif image := part.as_image():
                    image.save(
                        f"{output_dir}/{original_file_name}.mask.{attempt_idx}.raw.jpg"
                    )
                else:
                    pass

        except Exception as e:
            logger.warning(f"Generation for {original_file_name} failed: {e}")
            break


def get_img_id(image_path: Path) -> str:
    return image_path.stem.split(".")[0]


async def batch_processing(
    image_dir: Path,
    output_dir: Path,
    color_palette_path: Path,
    attempts: int,
    label_colors: List[List[int]] | None,
    client_idx: int | None,
):
    all_images = list(image_dir.glob("*.jpg"))
    processed_images = list(output_dir.glob(f"*.mask.{attempts - 1}.raw.jpg"))
    processed_image_names = {get_img_id(image) for image in processed_images}
    print(f"Processed {len(processed_image_names)} images before")
    all_images_todo = [
        image for image in all_images if get_img_id(image) not in processed_image_names
    ]
    todo_num = len(all_images_todo)
    print(f"Processing {todo_num} images")
    tasks = [
        gen_mask(
            image, color_palette_path, output_dir, attempts, label_colors, client_idx
        )
        for image in all_images_todo
    ]
    await tqdm_asyncio.gather(*tasks, desc="Generating masks", total=todo_num)


if __name__ == "__main__":
    asyncio.run(
        batch_processing(
            image_dir=IMAGE_DIR,
            output_dir=OUTPUT_DIR,
            color_palette_path=COLOR_PALETTE_PATH,
            attempts=ATTEMPTS,
            label_colors=None,
            client_idx=CLIENT_IDX,
        )
    )
