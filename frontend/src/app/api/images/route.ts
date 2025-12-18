import { promises as fs } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import {
  DATASETS,
  type DatasetId,
  DEFAULT_DATASET,
  isDatasetId,
} from "@/lib/datasets";

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const EVAL_ROOT = path.join(PROJECT_ROOT, "eval-set");
const STEM_RE = /^[a-zA-Z0-9_-]+$/;

type ImageItem = {
  stem: string;
  url: string;
};

type ImagesResponse = {
  dataset: DatasetId;
  images: ImageItem[];
};

export async function GET(request: Request): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(request.url);
    const datasetParam = searchParams.get("dataset");
    const dataset = isDatasetId(datasetParam) ? datasetParam : DEFAULT_DATASET;
    const config = DATASETS[dataset];
    const evalDir = path.join(EVAL_ROOT, config.evalSubDir);

    const stems = new Set<string>();

    for (const subDir of config.imageSubDirs) {
      const dirPath = path.join(evalDir, subDir);
      try {
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        for (const entry of entries) {
          if (!entry.isFile()) continue;
          if (!entry.name.endsWith(config.imageExtension)) continue;

          const stem = entry.name.slice(0, -config.imageExtension.length);
          if (STEM_RE.test(stem)) {
            stems.add(stem);
          }
        }
      } catch (error) {
        // Ignore missing directories
        if (
          typeof error === "object" &&
          error !== null &&
          "code" in error &&
          (error as { code?: string }).code === "ENOENT"
        ) {
          continue;
        }
        console.warn(`Failed to read directory ${dirPath}`, error);
      }
    }

    const images: ImageItem[] = Array.from(stems)
      .sort()
      .map((stem) => ({
        stem,
        url: `/api/file?dataset=${dataset}&stem=${stem}&kind=img`,
      }));

    const body: ImagesResponse = {
      dataset,
      images,
    };

    return NextResponse.json(body);
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
