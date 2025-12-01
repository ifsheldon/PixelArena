from asynciolimiter import Limiter
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio
import logging
from pixel_arena.dataset_utils.celeb_a_mask_hq import get_prompt as get_prompt_celeb
from pixel_arena.dataset_utils.coco import get_prompt as get_prompt_coco
from pathlib import Path
import base64
import os
from typing import Literal, List
from pydantic import ConfigDict, validate_call
import pickle


logger = logging.getLogger("generate_mask_gpt")


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def gen_mask(
    *,
    client: AsyncOpenAI,
    limiter: Limiter,
    dataset: Literal["celeb", "coco"],
    original_image_path: Path,
    color_palette_path: Path,
    output_dir: Path,
    attempts: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    original_file_name = original_image_path.stem
    todos = []
    for i in range(attempts):
        if os.path.exists(f"{output_dir}/{original_file_name}.mask.{i}.raw.png"):
            continue
        else:
            todos.append(i)

    if len(todos) == 0:
        return

    if dataset == "celeb":
        get_prompt = get_prompt_celeb
    else:
        get_prompt = get_prompt_coco

    await limiter.wait()
    try:
        n = len(todos)
        response = await client.images.edit(
            image=[
                # first image is the original image
                open(original_image_path, "rb"),
                # second image is the color palette, as mentioned in the prompt
                open(color_palette_path, "rb"),
            ],
            prompt=get_prompt(label_colors),
            model="gpt-image-1",
            n=n,
            size="1024x1024",
            quality="high",
            background="opaque",
            input_fidelity="high",
        )
    except Exception as e:
        logger.warning(f"Generation for {original_image_path} failed: {e}")
        return

    for idx, i in enumerate(todos):
        image_base64 = response.data[idx].b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(f"{output_dir}/{original_file_name}.mask.{i}.raw.png", "wb") as f:
            f.write(image_bytes)

        if save_response:
            with open(
                f"{output_dir}/{original_file_name}.mask.{i}.response.pkl", "wb"
            ) as f:
                pickle.dump(response, f)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def batch_gen_mask(
    *,
    image_dir: Path,
    output_dir: Path,
    color_palette_path: Path,
    attempts: int,
    dataset: Literal["celeb", "coco"],
    client: AsyncOpenAI,
    rpm: int,
    label_colors: List[List[int]] | None,
    save_response: bool,
):
    limiter = Limiter(rpm / 60)
    all_images = list(image_dir.glob("*.jpg"))
    tasks = [
        gen_mask(
            client=client,
            limiter=limiter,
            dataset=dataset,
            original_image_path=image,
            color_palette_path=color_palette_path,
            output_dir=output_dir,
            attempts=attempts,
            label_colors=label_colors,
            save_response=save_response,
        )
        for image in all_images
    ]
    await tqdm_asyncio.gather(
        *tasks, desc="Generating masks", total=len(all_images) * attempts
    )
