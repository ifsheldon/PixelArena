from pathlib import Path
from multiprocessing import Pool
from pixel_arena.metrics import RunInfo


gemini_pro_run_celeb = RunInfo(
    model_name="gemini-pro",
    model_code_name="gmn3",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-pro-150"),
    attempts=5,
    dataset="celeb",
)
gemini_pro_shuffled_run_celeb = RunInfo(
    model_name="gemini-pro-shuffled",
    model_code_name="gmn3-shuffled",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-pro-150-shuffled-label-colors"),
    attempts=5,
    dataset="celeb",
)
gemini_run_celeb = RunInfo(
    model_name="gemini",
    model_code_name="gmn25",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gemini-150"),
    attempts=5,
    dataset="celeb",
)
gpt_run_celeb = RunInfo(
    model_name="gpt-image",
    model_code_name="gpti",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/gpt-image-150"),
    attempts=5,
    dataset="celeb",
)
sam3_run_celeb = RunInfo(
    model_name="sam3",
    model_code_name="sam3",
    small_mask=True,
    pred_mask_path=Path("./results/celeb/sam3-150"),
    attempts=1,
    dataset="celeb",
)
segface_run_celeb = RunInfo(
    model_name="segface",
    model_code_name="segface",
    small_mask=True,
    pred_mask_path=Path("./results/celeb/segface-150"),
    attempts=1,
    dataset="celeb",
)
uni_moe_2_image_run_celeb = RunInfo(
    model_name="uni-moe-2-image",
    model_code_name="unimoe2-image",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/uni-moe-2-image-150"),
    attempts=1,
    dataset="celeb",
)
uni_moe_2_omni_run_celeb = RunInfo(
    model_name="uni-moe-2-omni",
    model_code_name="unimoe2-omni",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/uni-moe-2-omni-150"),
    attempts=1,
    dataset="celeb",
)

emu35_run_celeb = RunInfo(
    model_name="emu35",
    model_code_name="emu35",
    small_mask=False,
    pred_mask_path=Path("./results/celeb/emu35-150"),
    attempts=1,
    dataset="celeb",
)

celeb_runs = [
    uni_moe_2_image_run_celeb,
    uni_moe_2_omni_run_celeb,
    emu35_run_celeb,
    gemini_run_celeb,
    gemini_pro_run_celeb,
    gemini_pro_shuffled_run_celeb,
    gpt_run_celeb,
    sam3_run_celeb,
    segface_run_celeb,
]

gemini_pro_run_coco = RunInfo(
    model_name="gemini-pro",
    model_code_name="gmn3",
    small_mask=False,
    pred_mask_path=Path("./results/coco/gemini-pro-150"),
    attempts=5,
    dataset="coco",
)
gemini_run_coco = RunInfo(
    model_name="gemini",
    model_code_name="gmn25",
    small_mask=False,
    pred_mask_path=Path("./results/coco/gemini-150"),
    attempts=5,
    dataset="coco",
)

coco_runs = [
    gemini_pro_run_coco,
    gemini_run_coco,
]


def calc(run: RunInfo):
    run.calculate_and_save_metrics()


if __name__ == "__main__":
    runs = celeb_runs
    print(f"Calculating metrics for {len(runs)} runs")
    with Pool(len(runs)) as pool:
        pool.map(calc, runs)
