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
import os

# parameters when it's run in CLI
MODEL = "gemini-2.5-flash-image"
IMAGE_DIR = Path("./eval-set/images-150")
OUTPUT_DIR = Path("./results/gemini-150")
CLIENT_IDX = None
COLOR_PALETTE_PATH = Path("./label_palettes/seg-labels.png")
ATTEMPTS = 3
# end of parameters

CLIENTS = [
    # LF project default
    genai.Client(
        api_key="AIzaSyD00P48lTw9vZy2wEVGxxbsWJRJrTUVr3o",
    ).aio,
    # LF project openevolve
    genai.Client(
        api_key="AIzaSyC54rwWvN69P0scm1vEd4YRzk7smrPWzJs",
    ).aio,
    # Sizhe
    genai.Client(
        api_key="AIzaSyCqVg3CbqjJS1CERlnuz0pI36Y1JPEBEtI",
    ).aio,
    # LF project segmentation
    genai.Client(
        api_key="AIzaSyBGNIqo0lAhUArzXJnFgBibDzZ4BF_nmsc",
    ).aio,
    # LF project test
    genai.Client(
        api_key="AIzaSyBR4Hu6mfoHmJl9tT2RAZbcUujqsmt3VNA",
    ).aio,
]

RPM = 480  # tier 1 -> RPM = 500 with a bit buffer
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
    attempt_idx: int,
    label_colors: List[List[int]] | None,
    client_idx: int | None,
):
    original_file_name = original_image_path.stem
    save_file_path = f"{output_dir}/{original_file_name}.mask.{attempt_idx}.raw.jpg"

    if os.path.exists(save_file_path):
        logger.info(f"Mask for {original_file_name} already exists at {save_file_path}")
        return

    contents = [
        # first image is the original image
        Image.open(original_image_path).convert("RGB"),
        # second image is the color palette, as mentioned in the prompt
        Image.open(color_palette_path).convert("RGB"),
        get_prompt(label_colors),
    ]

    thinking_config = (
        types.ThinkingConfig(include_thoughts=True)
        if MODEL == "gemini-3-pro-image-preview"
        else None
    )
    image_size = "1K" if MODEL == "gemini-3-pro-image-preview" else None

    try:
        client = await get_client(client_idx)
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
            return

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
                image.save(save_file_path)
            else:
                pass

    except Exception as e:
        logger.warning(
            f"Generation for {original_file_name} (attempt {attempt_idx}) failed: {e}"
        )


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
    tasks = []
    
    for image in all_images:
        for attempt_idx in range(attempts):
            tasks.append(
                gen_mask(
                    original_image_path=image,
                    color_palette_path=color_palette_path,
                    output_dir=output_dir,
                    label_colors=label_colors,
                    client_idx=client_idx,
                    attempt_idx=attempt_idx,
                )
            )

    await tqdm_asyncio.gather(
        *tasks, desc="Generating masks", total=len(all_images) * attempts
    )


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
