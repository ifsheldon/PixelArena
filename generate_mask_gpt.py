from asynciolimiter import Limiter
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio
import logging
from prompt import get_prompt
from pathlib import Path
import base64
import asyncio

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
    await limiter.wait()
    try:
        response = await client.images.edit(
            image=[
                # first image is the original image
                open(original_image_path, "rb"),
                # second image is the color palette, as mentioned in the prompt
                open(color_palette_path, "rb"),
            ],
            prompt=get_prompt(),
            model="gpt-image-1",
            n=attempts,
            size="1024x1024",
            quality="high",
            background="opaque",
            input_fidelity="high",
        )
    except Exception as e:
        logger.warning(f"Generation for {original_image_path} failed: {e}")
        return

    original_file_name = original_image_path.stem

    for i in range(attempts):
        image_base64 = response.data[i].b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(f"{output_dir}/{original_file_name}.mask.{i}.raw.png", "wb") as f:
            f.write(image_bytes)


def get_img_id(image_path: Path) -> str:
    return image_path.stem.split(".")[0]


async def batch_processing():
    image_dir = Path("./eval-set/images-150")
    all_images = list(image_dir.glob("*.jpg"))
    color_palette_path = Path("seg-labels.png")
    output_dir = Path("gpt-image-test")
    attempts = 3
    processed_images = list(output_dir.glob(f"*.mask.{attempts - 1}.raw.png"))
    processed_image_names = {get_img_id(image) for image in processed_images}
    print(f"Processed {len(processed_image_names)} images before")
    all_images_todo = [
        image for image in all_images if get_img_id(image) not in processed_image_names
    ]
    todo_num = len(all_images_todo)
    print(f"Processing {todo_num} images")
    tasks = [
        gen_mask(image, color_palette_path, output_dir, attempts)
        for image in all_images_todo
    ]
    await tqdm_asyncio.gather(*tasks, desc="Generating masks", total=todo_num)


if __name__ == "__main__":
    asyncio.run(batch_processing())
