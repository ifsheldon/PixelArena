export const LABELS = [
  "background", // 0
  "skin", // 1
  "nose", // 2
  "eye_g", // 3
  "l_eye", // 4
  "r_eye", // 5
  "l_brow", // 6
  "r_brow", // 7
  "l_ear", // 8
  "r_ear", // 9
  "mouth", // 10
  "u_lip", // 11
  "l_lip", // 12
  "hair", // 13
  "hat", // 14
  "ear_r", // 15
  "neck_l", // 16
  "neck", // 17
  "cloth", // 18
] as const;

export type LabelIndex =
  | 0
  | 1
  | 2
  | 3
  | 4
  | 5
  | 6
  | 7
  | 8
  | 9
  | 10
  | 11
  | 12
  | 13
  | 14
  | 15
  | 16
  | 17
  | 18;

export const LABEL_COLORS: ReadonlyArray<readonly [number, number, number]> = [
  [0, 0, 0], // 0 background
  [204, 0, 0], // 1 skin
  [76, 153, 0], // 2 nose
  [204, 204, 0], // 3 eye_g
  [51, 51, 255], // 4 l_eye
  [204, 0, 204], // 5 r_eye
  [0, 255, 255], // 6 l_brow
  [255, 204, 204], // 7 r_brow
  [102, 51, 0], // 8 l_ear
  [255, 0, 0], // 9 r_ear
  [102, 204, 0], // 10 mouth
  [255, 255, 0], // 11 u_lip
  [0, 0, 153], // 12 l_lip
  [0, 0, 204], // 13 hair
  [255, 51, 153], // 14 hat
  [0, 204, 204], // 15 ear_r
  [0, 51, 0], // 16 neck_l
  [255, 153, 51], // 17 neck
  [0, 204, 0], // 18 cloth
] as const;

export const NUM_CLASSES = LABELS.length as 19;

const colorKey = (r: number, g: number, b: number): string => `${r},${g},${b}`;

const colorToIndex = new Map<string, LabelIndex>(
  LABEL_COLORS.map((rgb, idx) => [
    colorKey(rgb[0], rgb[1], rgb[2]),
    idx as LabelIndex,
  ]),
);

export function getLabelByRGB(
  r: number,
  g: number,
  b: number,
): { index: LabelIndex; name: (typeof LABELS)[LabelIndex] } | undefined {
  const idx = colorToIndex.get(colorKey(r, g, b));
  if (idx === undefined) return undefined;
  return { index: idx, name: LABELS[idx] };
}
