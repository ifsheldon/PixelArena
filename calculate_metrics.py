from pathlib import Path
from multiprocessing import Pool
from pixel_arena.metrics import RunInfo


gemini_pro_run_celeb = RunInfo(
    model_name="gemini-pro",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-pro-150"),
    attempts=5,
    dataset="celeb",
)
gemini_pro_shuffled_run_celeb = RunInfo(
    model_name="gemini-pro-shuffled",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-pro-150-shuffled-label-colors"),
    attempts=5,
    dataset="celeb",
)
gemini_run_celeb = RunInfo(
    model_name="gemini",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-150"),
    attempts=5,
    dataset="celeb",
)
gpt_run_celeb = RunInfo(
    model_name="gpt-image",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gpt-image-150"),
    attempts=5,
    dataset="celeb",
)
sam3_run_celeb = RunInfo(
    model_name="sam3",
    small_mask=True,
    pred_mask_path=Path("./results/celeb/sam3-150"),
    attempts=1,
    dataset="celeb",
)
segface_run_celeb = RunInfo(
    model_name="segface",
    small_mask=True,
    pred_mask_path=Path("./results/celeb/segface-150"),
    attempts=1,
    dataset="celeb",
)
uni_moe_2_image_run_celeb = RunInfo(
    model_name="uni-moe-2-image",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/uni-moe-2-image-150"),
    attempts=1,
    dataset="celeb",
)
uni_moe_2_omni_run_celeb = RunInfo(
    model_name="uni-moe-2-omni",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/uni-moe-2-omni-150"),
    attempts=1,
    dataset="celeb",
)
# emu35_run_celeb = RunInfo(
#     model_name="emu35",
#     small_mask=True,
#     pred_mask_path=Path("./results/celeb/emu35-150"),
#     attempts=1,
#     dataset="celeb",
# )

celeb_runs = [
    gemini_pro_run_celeb,
    gemini_pro_shuffled_run_celeb,
    gemini_run_celeb,
    gpt_run_celeb,
    uni_moe_2_image_run_celeb,
    uni_moe_2_omni_run_celeb,
    sam3_run_celeb,
    segface_run_celeb,
]

gemini_pro_run_coco = RunInfo(
    model_name="gemini-pro",
    small_mask=False,
    pred_mask_path=Path("./results/coco/gemini-pro-150"),
    attempts=5,
    dataset="coco",
)
gemini_run_coco = RunInfo(
    model_name="gemini",
    small_mask=False,
    pred_mask_path=Path("./results/coco/gemini-150"),
    attempts=5,
    dataset="coco",
)

coco_runs = [
    gemini_pro_run_coco,
    gemini_run_coco,
]


if __name__ == "__main__":
    runs = coco_runs

    def calc(run: RunInfo):
        run.calculate_and_save_metrics()

    with Pool(len(runs)) as pool:
        pool.map(calc, runs)
