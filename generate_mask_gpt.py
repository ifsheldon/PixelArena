from openai import AsyncOpenAI
from pixel_arena.generation.gpt import batch_gen_mask
import logging
from pathlib import Path
import asyncio

logging.basicConfig(level=logging.WARNING)


if __name__ == "__main__":
    asyncio.run(
        batch_gen_mask(
            image_dir=Path("./eval-set/celeb/images-150"),
            output_dir=Path("./results/celeb/gpt-image-150"),
            color_palette_path=Path("./label_palettes/seg_labels_celeb.png"),
            attempts=5,
            dataset="celeb",
            client=AsyncOpenAI(),
            rpm=42,  # tier 3 -> RPM = 50 with a bit buffer
            label_colors=None,
            save_response=False,
        )
    )
