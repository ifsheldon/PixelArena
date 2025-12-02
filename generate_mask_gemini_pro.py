"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from pixel_arena.generation.gemini import batch_gen_mask
from pathlib import Path
import asyncio
import logging
from clients import gemini_clients

logging.basicConfig(level=logging.WARNING)


if __name__ == "__main__":
    asyncio.run(
        batch_gen_mask(
            rpm=12,  # tier 1 -> RPM = 20 with a bit buffer
            model="gemini-3-pro-image-preview",
            image_dir=Path("./eval-set/celeb/images-150"),
            output_dir=Path("./results/gemini-pro-150"),
            color_palette_path=Path("./label_palettes/seg_labels_celeb.png"),
            attempts=5,
            label_colors=None,
            save_response=False,
            dataset="celeb",
            clients=gemini_clients,
        )
    )
