"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google.genai import types
from google.genai.client import AsyncClient
from pathlib import Path
from PIL import Image
from tqdm.asyncio import tqdm_asyncio
import random
from pixel_arena.dataset_utils.celeb_a_mask_hq import get_prompt as get_prompt_celeb
from pixel_arena.dataset_utils.coco import get_prompt as get_prompt_coco
from asynciolimiter import Limiter
from typing import List, Literal
import os
import pickle
import logging
from pydantic import ConfigDict, validate_call
from pixel_arena.image_processing import mask_raw_to_pmode

logger = logging.getLogger("generate_mask_gemini")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def gen_mask(
    *,
    client: AsyncClient,
    limiter: Limiter,
    model: Literal["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
    dataset: Literal["celeb", "coco"],
    original_image_path: Path,
    color_palette_path: Path | List[Path],
    output_dir: Path,
    attempt_idx: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    original_file_name = original_image_path.stem
    save_raw_file_path = f"{output_dir}/{original_file_name}.mask.{attempt_idx}.raw.jpg"
    save_pmode_file_path = f"{output_dir}/{original_file_name}.mask.{attempt_idx}.pred.png"

    raw_file_exists = os.path.exists(save_raw_file_path)
    pmode_file_exists = os.path.exists(save_pmode_file_path)

    if raw_file_exists and pmode_file_exists:
        logger.info(f"Mask for {original_file_name} already exists at {save_raw_file_path} and {save_pmode_file_path}")
        return
    
    if raw_file_exists and not pmode_file_exists:
        mask_pmode = mask_raw_to_pmode(save_raw_file_path, dataset, label_colors)
        mask_pmode.save(save_pmode_file_path)
        return

    save_response_path = (
        f"{output_dir}/{original_file_name}.mask.{attempt_idx}.response.pkl"
    )

    if dataset == "celeb":
        assert isinstance(color_palette_path, Path), (
            "Color palette path should be a single path for celeb dataset"
        )
        contents = [
            # first image is the original image
            Image.open(original_image_path).convert("RGB"),
            # second image is the color palette, as mentioned in the prompt
            Image.open(color_palette_path).convert("RGB"),
            get_prompt_celeb(label_colors),
        ]
    else:
        assert isinstance(color_palette_path, list), (
            "Color palette path should be a list of paths for coco dataset"
        )
        palettes = [Image.open(p).convert("RGB") for p in color_palette_path]
        contents = [
            # first image is the original image
            Image.open(original_image_path).convert("RGB"),
            *palettes,
            get_prompt_coco(label_colors),
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
                image.save(save_raw_file_path)
                mask_pmode = mask_raw_to_pmode(save_raw_file_path, dataset, label_colors)
                mask_pmode.save(save_pmode_file_path)
            else:
                pass

        if save_response:
            with open(save_response_path, "wb") as f:
                pickle.dump(response, f)

    except Exception as e:
        logger.warning(
            f"Generation for {original_file_name} (attempt {attempt_idx}) failed: {e}"
        )


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def batch_gen_mask(
    *,
    clients: List[AsyncClient] | AsyncClient,
    rpm: int,
    model: Literal["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
    dataset: Literal["celeb", "coco"],
    image_dir: Path,
    output_dir: Path,
    color_palette_path: Path | List[Path],
    attempts: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    all_images = list(image_dir.glob("*.jpg"))
    if isinstance(clients, AsyncClient):
        clients = [clients]
    limiters = [Limiter(rpm / 60) for _ in range(len(clients))]
    tasks = []
    if dataset == "celeb":
        assert isinstance(color_palette_path, Path), (
            "Color palette path should be a single path for celeb dataset"
        )
    else:
        assert isinstance(color_palette_path, list), (
            "Color palette path should be a list of paths for coco dataset"
        )

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
