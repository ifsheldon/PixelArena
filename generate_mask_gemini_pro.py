"""
This generates raw masks that are colorful jpeg using Gemini.
"""

from google import genai
from pixel_arena.generation.gemini import batch_gen_mask
from pathlib import Path
import asyncio
import logging

logging.basicConfig(level=logging.WARNING)


if __name__ == "__main__":
    asyncio.run(
        batch_gen_mask(
            rpm=12,  # tier 1 -> RPM = 20 with a bit buffer
            model="gemini-3-pro-image-preview",
            image_dir=Path("./eval-set/images-150"),
            output_dir=Path("./results/gemini-pro-150"),
            color_palette_path=Path("./label_palettes/seg-labels.png"),
            attempts=5,
            label_colors=None,
            save_response=False,
            dataset="celeb",
            clients=[
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
            ],
        )
    )
