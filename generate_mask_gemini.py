"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google import genai
from pixel_arena.generation.gemini import batch_gen_mask
from pathlib import Path
import asyncio
import logging


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
            clients=[
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
            ],
        )
    )
