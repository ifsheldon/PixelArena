import torch
from PIL import Image
from torchvision import transforms
from pathlib import Path
from functools import cache
from torchmetrics.functional.classification import multiclass_f1_score
from torchmetrics.functional.segmentation import mean_iou, dice_score
from typing import List, Literal
import pickle
from tqdm.auto import tqdm

to_tensor = transforms.PILToTensor()


@cache
def get_image(path: Path, return_image: bool) -> Image.Image:
    mask = Image.open(path)
    if return_image:
        return mask
    mask = to_tensor(mask)
    return mask


class RunInfo:
    def __init__(
        self,
        *,
        model_name: str,
        model_code_name: str,
        small_mask: bool,
        pred_mask_path: Path,
        attempts: int,
        dataset: Literal["celeb", "coco"],
    ):
        self.model_name = model_name
        self.model_code_name = model_code_name
        self.small_mask = small_mask
        self.pred_mask_path = pred_mask_path
        assert pred_mask_path.exists()
        self.attempts = attempts
        self.dataset = dataset
        self.mask_transform = transforms.PILToTensor()
        self.save_metric_path = Path(
            f"saved_result_binary/metrics/{dataset}/{model_name}.metrics.pkl"
        )

        if dataset == "celeb":
            image_path = Path("./eval-set/celeb/images-150/")
            assert image_path.exists()
        else:
            image_path = Path("./eval-set/coco/images-150/")
            assert image_path.exists()
        self.image_path = image_path
        image_ids = {image.stem for image in image_path.glob("*.jpg")}
        self.image_ids = sorted(list(image_ids))

        if dataset == "celeb":
            self.ref_masks_path = (
                Path("./eval-set/celeb/masks-512/")
                if small_mask
                else Path("./eval-set/celeb/masks-1024/")
            )
            self.class_max = 18
            self.label_num = 19
        else:
            assert not small_mask
            self.ref_masks_path = Path("./eval-set/coco/masks-1024/")
            self.class_max = 200
            self.label_num = 201
        assert self.ref_masks_path.exists()

    def __str__(self) -> str:
        return f"""
RunInfo:
    model_name: {self.model_name}
    small_mask: {self.small_mask}
    pred_mask_path: {self.pred_mask_path}
    attempts: {self.attempts}
    dataset: {self.dataset}
    save_metric_path: {self.save_metric_path}
"""

    def get_original_image(self, image_id: str) -> Image.Image:
        return get_image(self.image_path / f"{image_id}.jpg", return_image=True)

    def get_mask_ref(
        self, *, image_id: str, return_image: bool
    ) -> torch.Tensor | Image.Image:
        ref_mask_path = self.ref_masks_path / f"{image_id}.png"
        mask = get_image(ref_mask_path, return_image)
        if return_image:
            return mask
        assert mask.dtype == torch.uint8
        assert mask.max() <= self.class_max
        return mask

    def get_mask_preds(
        self, *, image_id: str, return_image: bool
    ) -> List[torch.Tensor] | List[Image.Image]:
        result_path = self.pred_mask_path
        masks = []
        for i in range(self.attempts):
            mask_path = result_path / f"{image_id}.mask.{i}.pred.png"
            mask = Image.open(mask_path)
            if return_image:
                masks.append(mask)
                continue
            mask = self.mask_transform(mask)
            assert mask.dtype == torch.uint8
            assert mask.max() <= self.class_max
            masks.append(mask)
        return masks

    def calculate_and_save_metrics(self, force_recalculate: bool = False):
        if not force_recalculate and self.save_metric_path.exists():
            self.load_metrics()
            print(f"Metrics already calculated.\n{self}")
            return
        
        f1_scores = []
        iou_scores = []
        dice_scores = []
        for image_id in tqdm(self.image_ids):
            mask_ref = self.get_mask_ref(image_id=image_id, return_image=False)
            masks_pred = self.get_mask_preds(image_id=image_id, return_image=False)
            assert mask_ref.shape == masks_pred[0].shape

            f1_score = torch.empty(self.attempts)
            for i, mask_pred in enumerate(masks_pred):
                f1 = multiclass_f1_score(
                    mask_pred, mask_ref, num_classes=self.label_num, average="macro"
                )
                f1_score[i] = f1
            f1_scores.append(f1_score)

            mask_ref = mask_ref.long()
            for i in range(self.attempts):
                masks_pred[i] = masks_pred[i].long()

            iou_score = torch.empty(self.attempts)
            for i, mask_pred in enumerate(masks_pred):
                iou = mean_iou(
                    mask_pred,
                    mask_ref,
                    num_classes=self.label_num,
                    input_format="index",
                )
                iou_score[i] = iou
            iou_scores.append(iou_score)

            dice = torch.empty(self.attempts)
            for i, mask_pred in enumerate(masks_pred):
                d = dice_score(
                    mask_pred,
                    mask_ref,
                    num_classes=self.label_num,
                    average="macro",
                    input_format="index",
                )
                dice[i] = d
            dice_scores.append(dice)

        f1_scores = torch.stack(f1_scores)
        iou_scores = torch.stack(iou_scores)
        dice_scores = torch.stack(dice_scores)
        self.f1_scores = f1_scores
        self.iou_scores = iou_scores
        self.dice_scores = dice_scores
        with open(self.save_metric_path, "wb") as f:
            metrics = {
                "f1": f1_scores,
                "iou": iou_scores,
                "dice": dice_scores,
            }
            pickle.dump(metrics, f)

    def load_metrics(self):
        with open(self.save_metric_path, "rb") as f:
            metrics = pickle.load(f)
        self.f1_scores = metrics["f1"]
        self.iou_scores = metrics["iou"]
        self.dice_scores = metrics["dice"]
        return self.f1_scores, self.iou_scores, self.dice_scores
