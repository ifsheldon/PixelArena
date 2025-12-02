import type { DatasetId } from "./datasets";
import { CELEB_LABEL_COLORS, CELEB_LABELS } from "./palettes/celeb";
import { COCO_LABEL_COLORS, COCO_LABELS } from "./palettes/coco";

type LabelName = string | null;

type DatasetLabelInfo = {
  labels: readonly LabelName[];
  colorMap: Map<string, { index: number; name: string }>;
};

const colorKey = (r: number, g: number, b: number): string => `${r},${g},${b}`;

const createLabelInfo = (
  labels: readonly LabelName[],
  colors: ReadonlyArray<readonly [number, number, number]>,
): DatasetLabelInfo => {
  if (labels.length !== colors.length) {
    throw new Error(
      `Label and color length mismatch: ${labels.length} vs ${colors.length}`,
    );
  }
  const colorMap = new Map<string, { index: number; name: string }>();
  colors.forEach((rgb, idx) => {
    const key = colorKey(rgb[0], rgb[1], rgb[2]);
    if (colorMap.has(key)) {
      return;
    }
    const fallback = labels[idx] ?? `unused-${idx}`;
    colorMap.set(key, { index: idx, name: fallback });
  });
  return { labels, colorMap };
};

const DATASET_LABELS: Record<DatasetId, DatasetLabelInfo> = {
  celeb: createLabelInfo(CELEB_LABELS, CELEB_LABEL_COLORS),
  coco: createLabelInfo(COCO_LABELS, COCO_LABEL_COLORS),
};

export function getDatasetLabels(datasetId: DatasetId): readonly string[] {
  const data = DATASET_LABELS[datasetId];
  return data.labels.filter(
    (label): label is string => typeof label === "string" && label.length > 0,
  );
}

export function getLabelByRGB(
  datasetId: DatasetId,
  r: number,
  g: number,
  b: number,
): { index: number; name: string } | undefined {
  const data = DATASET_LABELS[datasetId];
  return data.colorMap.get(colorKey(r, g, b));
}
