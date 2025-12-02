"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google import genai
from pixel_arena.generation.gemini import batch_gen_mask
from pathlib import Path
import asyncio
import logging
from clients import gemini_clients


logger = logging.getLogger("generate_mask_gemini")
logging.basicConfig(level=logging.WARNING)


if __name__ == "__main__":
    asyncio.run(
        batch_gen_mask(
            rpm=480,  # tier 1 -> RPM = 500 with a bit buffer
            model="gemini-2.5-flash-image",
            image_dir=Path("./eval-set/images-150"),
            output_dir=Path("./results/gemini-150"),
            color_palette_path=Path("./label_palettes/seg_labels_celeb.png"),
            attempts=5,
            label_colors=None,
            save_response=False,
            dataset="celeb",
            clients=gemini_clients,
        )
    )
