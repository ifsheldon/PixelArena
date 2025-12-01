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
from pixel_arena.dataset_utils.celeb_a_mask_hq import get_prompt as get_prompt_celeb
from pixel_arena.dataset_utils.coco import get_prompt as get_prompt_coco
from asynciolimiter import Limiter
from typing import List, Literal
import os
import pickle

# parameters when it's run in CLI
MODEL = "gemini-3-pro-image-preview"
IMAGE_DIR = Path("./eval-set/images-150")
OUTPUT_DIR = Path("./results/gemini-pro-150")
CLIENT_IDX = None
COLOR_PALETTE_PATH = Path("./label_palettes/seg-labels.png")
ATTEMPTS = 5
# end of parameters

CLIENTS = [
    # Sizhe
    genai.Client(
        api_key="AIzaSyCqVg3CbqjJS1CERlnuz0pI36Y1JPEBEtI",
    ).aio,
    # Sizhe
    genai.Client(
        api_key="AIzaSyB1nR_Q1Y-LrbsJnccKXR_gQ7HhsyE8IdA",
    ).aio,
    # Sizhe
    genai.Client(
        api_key="AIzaSyC-FKheOYGSVmMQasQcd3tkUvIX1JbIrzs",
    ).aio,
    # Sizhe
    genai.Client(
        api_key="AIzaSyDjU-aRcLrY4wV03PnZ5wN6H8xp_t6N3SA",
    ).aio,
    # LF project default
    genai.Client(
        api_key="AIzaSyD00P48lTw9vZy2wEVGxxbsWJRJrTUVr3o",
    ).aio,
    # LF project openevolve
    genai.Client(
        api_key="AIzaSyC54rwWvN69P0scm1vEd4YRzk7smrPWzJs",
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

RPM = 12  # tier 1 -> RPM = 20 with a bit buffer

logger = logging.getLogger("generate_mask_gemini")
logging.basicConfig(level=logging.WARNING)


async def gen_mask(
    *,
    client: AsyncClient,
    limiter: Limiter,
    model: Literal["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
    dataset: Literal["celeb", "coco"],
    original_image_path: Path,
    color_palette_path: Path,
    output_dir: Path,
    attempt_idx: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    assert model in ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"]
    assert dataset in ["celeb", "coco"]
    if dataset == "celeb":
        get_prompt = get_prompt_celeb
    else:
        get_prompt = get_prompt_coco
    original_file_name = original_image_path.stem
    save_file_path = f"{output_dir}/{original_file_name}.mask.{attempt_idx}.raw.jpg"
    save_response_path = (
        f"{output_dir}/{original_file_name}.mask.{attempt_idx}.response.pkl"
    )

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
        if model == "gemini-3-pro-image-preview"
        else None
    )
    image_size = "1K" if model == "gemini-3-pro-image-preview" else None

    try:
        await limiter.wait()
        response = await client.models.generate_content(
            model=model,
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
            if image := part.as_image():
                image.save(save_file_path)
            else:
                pass

        if save_response:
            with open(save_response_path, "wb") as f:
                pickle.dump(response, f)

    except Exception as e:
        logger.warning(
            f"Generation for {original_file_name} (attempt {attempt_idx}) failed: {e}"
        )


async def batch_processing(
    *,
    clients: List[AsyncClient] | AsyncClient,
    rpm: int,
    model: Literal["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
    dataset: Literal["celeb", "coco"],
    image_dir: Path,
    output_dir: Path,
    color_palette_path: Path,
    attempts: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    all_images = list(image_dir.glob("*.jpg"))
    if isinstance(clients, AsyncClient):
        clients = [clients]
    limiters = [Limiter(rpm / 60) for _ in range(len(clients))]
    tasks = []

    for image in all_images:
        for attempt_idx in range(attempts):
            idx = random.randint(0, len(clients) - 1)
            client = clients[idx]
            limiter = limiters[idx]
            tasks.append(
                gen_mask(
                    client=client,
                    limiter=limiter,
                    model=model,
                    dataset=dataset,
                    original_image_path=image,
                    color_palette_path=color_palette_path,
                    output_dir=output_dir,
                    label_colors=label_colors,
                    attempt_idx=attempt_idx,
                    save_response=save_response,
                )
            )

    await tqdm_asyncio.gather(
        *tasks, desc="Generating masks", total=len(all_images) * attempts
    )


if __name__ == "__main__":
    asyncio.run(
        batch_processing(
            clients=CLIENTS,
            rpm=RPM,
            model=MODEL,
            image_dir=IMAGE_DIR,
            output_dir=OUTPUT_DIR,
            color_palette_path=COLOR_PALETTE_PATH,
            attempts=ATTEMPTS,
            label_colors=None,
            save_response=False,
            dataset="celeb",
        )
    )
