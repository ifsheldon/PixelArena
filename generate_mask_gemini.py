"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google import genai
from google.genai import types
from google.genai.client import AsyncClient
from pathlib import Path
from PIL import Image
import asyncio
import tqdm
import random
import logging
from prompt import PROMPT

logger = logging.getLogger("generate_mask_gemini")

logging.basicConfig(level=logging.WARNING)

client0 = genai.Client(
    api_key="AIzaSyC54rwWvN69P0scm1vEd4YRzk7smrPWzJs",
).aio

client1 = genai.Client(
    api_key="AIzaSyCqVg3CbqjJS1CERlnuz0pI36Y1JPEBEtI",
).aio


def get_client(idx=None) -> AsyncClient:
    if idx is not None:
        return [client0, client1][idx]
    if random.random() < 0.5:
        return client0
    return client1


model = "gemini-3-pro-image-preview"
# model = "gemini-2.5-flash-image"


async def gen_mask(
    original_image_path: Path,
    color_palette_path: Path,
    output_dir: Path,
    attempts: int,
):
    contents = [
        # first image is the original image
        Image.open(original_image_path).convert("RGB"),
        # second image is the color palette, as mentioned in the prompt
        Image.open(color_palette_path).convert("RGB"),
        PROMPT,
    ]

    original_file_name = original_image_path.stem

    thinking_config = (
        types.ThinkingConfig(include_thoughts=True)
        if model == "gemini-3-pro-image-preview"
        else None
    )
    image_size = "1K" if model == "gemini-3-pro-image-preview" else None

    for attempt_idx in range(attempts):
        client = get_client()

        try:
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
        except Exception as e:
            logger.warning(f"Generation for {original_file_name} failed: {e}")
            break

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

        await asyncio.sleep(2)


def get_img_id(image_path: Path) -> str:
    return image_path.stem.split(".")[0]


async def batch_processing():
    image_dir = Path("./eval-set/images")
    all_images = list(image_dir.glob("*.jpg"))
    batch_size = 5
    color_palette_path = Path("seg-labels.png")
    output_dir = Path("test")
    attempts = 3
    processed_images = list(output_dir.glob(f"*.mask.{attempts - 1}.raw.jpg"))
    processed_image_names = {get_img_id(image) for image in processed_images}
    print(f"Processed {len(processed_image_names)} images before")
    all_images_todo = [
        image for image in all_images if get_img_id(image) not in processed_image_names
    ]
    print(f"Processing {len(all_images_todo)} images")
    for i in tqdm.tqdm(range(0, len(all_images_todo), batch_size)):
        batch_images = all_images_todo[i : i + batch_size]
        await asyncio.gather(
            *[
                gen_mask(image, color_palette_path, output_dir, attempts)
                for image in batch_images
            ]
        )
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(batch_processing())
