import math
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


def plot_label_palette(labels, colors, columns=3, save_path=None):
    rows = math.ceil(len(labels) / columns)

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

    for idx, (label, color) in enumerate(zip(labels, colors)):
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
        plt.savefig(save_path)

    plt.show()
