export const DATASET_IDS = ["celeb", "coco"] as const;

export type DatasetId = (typeof DATASET_IDS)[number];

type DatasetConfig = {
  id: DatasetId;
  label: string;
  evalSubDir: string;
  resultsSubDir: string;
  imageSubDirs: readonly string[];
  imageExtension: ".jpg" | ".png";
  imageContentType: string;
  maskSubDir: string;
  maskExtension: ".png";
  maskContentType: string;
};

export const DATASETS: Record<DatasetId, DatasetConfig> = {
  celeb: {
    id: "celeb",
    label: "CelebAMask-HQ",
    evalSubDir: "celeb",
    resultsSubDir: "celeb",
    imageSubDirs: ["images", "images-150"],
    imageExtension: ".jpg",
    imageContentType: "image/jpeg",
    maskSubDir: "masks-1024",
    maskExtension: ".png",
    maskContentType: "image/png",
  },
  coco: {
    id: "coco",
    label: "COCO",
    evalSubDir: "coco",
    resultsSubDir: "coco",
    imageSubDirs: ["images-150"],
    imageExtension: ".jpg",
    imageContentType: "image/jpeg",
    maskSubDir: "masks-1024",
    maskExtension: ".png",
    maskContentType: "image/png",
  },
} as const;

export const DATASET_OPTIONS = DATASET_IDS.map((id) => ({
  id,
  label: DATASETS[id].label,
}));

export const DEFAULT_DATASET: DatasetId = "celeb";

export const DATASET_LABEL_LOOKUP = Object.fromEntries(
  DATASET_OPTIONS.map(({ id, label }) => [id, label]),
) as Record<DatasetId, string>;

export const isDatasetId = (value: string | null): value is DatasetId =>
  (value ?? "") === "celeb" || (value ?? "") === "coco";

export const getDatasetLabel = (datasetId: DatasetId): string =>
  DATASET_LABEL_LOOKUP[datasetId];
