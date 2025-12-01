from asynciolimiter import Limiter
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio
import logging
from pixel_arena.dataset_utils.celeb_a_mask_hq import get_prompt
from pathlib import Path
import base64
import asyncio
import os

RPM = 42  # tier 3 -> RPM = 50 with a bit buffer

limiter = Limiter(RPM / 60)
client = AsyncOpenAI()
logger = logging.getLogger("generate_mask_gpt")

logging.basicConfig(level=logging.WARNING)


async def gen_mask(
    original_image_path: Path,
    color_palette_path: Path,
    output_dir: Path,
    attempts: int,
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
            prompt=get_prompt(),
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


async def batch_processing():
    image_dir = Path("./eval-set/images-150")
    all_images = list(image_dir.glob("*.jpg"))
    color_palette_path = Path("./label_palettes/seg-labels.png")
    output_dir = Path("./results/gpt-image-150")
    attempts = 5
    tasks = [
        gen_mask(image, color_palette_path, output_dir, attempts)
        for image in all_images
    ]
    await tqdm_asyncio.gather(
        *tasks, desc="Generating masks", total=len(all_images) * attempts
    )


if __name__ == "__main__":
    asyncio.run(batch_processing())
