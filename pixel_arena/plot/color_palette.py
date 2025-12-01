import math
import os
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from typing import List


def plot_label_palette(
    labels: List[str | None],
    colors: List[List[int]],
    columns: int = 3,
    row_limit_per_image: int | None = None,
    save_path: str | None = None,
):
    valid_labels = []
    valid_colors = []
    for label, color in zip(labels, colors):
        if label is not None:
            valid_labels.append(label)
            valid_colors.append(color)

    labels = valid_labels
    colors = valid_colors
    total_items = len(labels)
    if row_limit_per_image is None or row_limit_per_image <= 0:
        items_per_page = total_items
    else:
        items_per_page = row_limit_per_image * columns

    if total_items == 0:
        return

    num_pages = math.ceil(total_items / items_per_page)

    for page_idx in range(num_pages):
        start_idx = page_idx * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        current_labels = labels[start_idx:end_idx]
        current_colors = colors[start_idx:end_idx]

        rows = math.ceil(len(current_labels) / columns)

        card_size = 1.1
        label_offset = 0.3
        cell_width = card_size + 0.9
        cell_height = card_size + label_offset + 0.8
        side_margin = 0.3
        top_margin = 0.3

        palette_width = side_margin * 2 + columns * cell_width
        palette_height = top_margin + rows * cell_height

        fig_width = columns * 2.5
        fig_height = rows * 2.2
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), constrained_layout=True)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.set_xlim(0, palette_width)
        ax.set_ylim(0, palette_height)
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.axis("off")

        for idx, (label, color) in enumerate(zip(current_labels, current_colors)):
            row = idx // columns
            col = idx % columns

            x = side_margin + col * cell_width + (cell_width - card_size) / 2
            y = top_margin + row * cell_height

            normalized_color = [c / 255.0 for c in color]
            rect = Rectangle(
                (x, y),
                card_size,
                card_size,
                facecolor=normalized_color,
                edgecolor="black",
                linewidth=0.1,
            )
            ax.add_patch(rect)

            label_y = y + card_size + label_offset
            ax.text(
                x + card_size / 2,
                label_y,
                label,
                ha="center",
                va="top",
                fontsize=12,
                color="black",
                weight="bold",
            )

        if save_path is not None:
            if num_pages > 1:
                root, ext = os.path.splitext(save_path)
                current_save_path = f"{root}_{page_idx + 1}{ext}"
            else:
                current_save_path = save_path
            plt.savefig(current_save_path)

        plt.show()
