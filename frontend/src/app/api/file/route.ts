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
const RESULTS_ROOT = path.join(PROJECT_ROOT, "results");
const STEM_RE = /^[a-zA-Z0-9_-]+$/;
const RUN_RE = /^[a-zA-Z0-9._-]+$/;

type ResolveParams = {
  dataset: DatasetId;
  stem: string;
  kind: "img" | "ref" | "pred";
  run?: string;
  attempt?: number;
};

const findExistingFile = async (
  candidates: string[],
): Promise<string | null> => {
  for (const candidate of candidates) {
    try {
      await fs.stat(candidate);
      return candidate;
    } catch (error: unknown) {
      if (
        typeof error === "object" &&
        error !== null &&
        "code" in error &&
        (error as { code?: string }).code === "ENOENT"
      ) {
        continue;
      }
      throw error;
    }
  }
  return null;
};

const resolvePath = async ({
  dataset,
  stem,
  kind,
  run,
  attempt,
}: ResolveParams): Promise<
  { abs: string; contentType: string } | undefined
> => {
  const config = DATASETS[dataset];
  const evalDir = path.join(EVAL_ROOT, config.evalSubDir);

  if (!STEM_RE.test(stem)) {
    return undefined;
  }

  if (kind === "img") {
    const candidates = config.imageSubDirs.map((dir) =>
      path.join(evalDir, dir, `${stem}${config.imageExtension}`),
    );
    const found = await findExistingFile(candidates);
    if (!found) return undefined;
    return { abs: found, contentType: config.imageContentType };
  }

  if (kind === "ref") {
    return {
      abs: path.join(
        evalDir,
        config.maskSubDir,
        `${stem}${config.maskExtension}`,
      ),
      contentType: config.maskContentType,
    };
  }

  if (kind === "pred") {
    if (!run || !RUN_RE.test(run) || attempt === undefined || attempt < 0) {
      return undefined;
    }
    const abs = path.join(
      RESULTS_ROOT,
      config.resultsSubDir,
      run,
      `${stem}.mask.${attempt}.pred.png`,
    );
    return { abs, contentType: "image/png" };
  }

  return undefined;
};

export async function GET(request: Request): Promise<NextResponse> {
  const { searchParams } = new URL(request.url);
  const stem = searchParams.get("stem");
  const kindParam = searchParams.get("kind");
  const datasetParam = searchParams.get("dataset");
  const runParam = searchParams.get("run");
  const attemptParam = searchParams.get("attempt");

  if (!stem || !kindParam) {
    return NextResponse.json(
      { error: "Missing stem or kind" },
      { status: 400 },
    );
  }

  if (kindParam !== "img" && kindParam !== "ref" && kindParam !== "pred") {
    return NextResponse.json({ error: "Invalid kind" }, { status: 400 });
  }

  const dataset = isDatasetId(datasetParam) ? datasetParam : DEFAULT_DATASET;
  const attempt =
    attemptParam !== null ? Number.parseInt(attemptParam, 10) : undefined;

  if (attemptParam !== null && Number.isNaN(attempt)) {
    return NextResponse.json({ error: "Invalid attempt" }, { status: 400 });
  }

  const resolved = await resolvePath({
    dataset,
    stem,
    kind: kindParam,
    run: runParam ?? undefined,
    attempt,
  });

  if (!resolved) {
    return NextResponse.json({ error: "Invalid parameters" }, { status: 400 });
  }

  try {
    const buffer = await fs.readFile(resolved.abs);
    const arrayBuffer = buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength,
    );
    return new NextResponse(arrayBuffer, {
      headers: {
        "Content-Type": resolved.contentType,
        "Cache-Control": "public, max-age=60",
      },
    });
  } catch (_error) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
}
