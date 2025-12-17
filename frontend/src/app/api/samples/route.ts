import { promises as fs } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import {
  DATASETS,
  type DatasetId,
  DEFAULT_DATASET,
  isDatasetId,
} from "@/lib/datasets";

type Sample = {
  stem: string;
  imageUrl: string;
  refUrl: string;
  predUrls: string[];
};

type SamplesResponse = {
  dataset: DatasetId;
  run: string | null;
  runs: string[];
  samples: Sample[];
};

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const RESULTS_ROOT = path.join(PROJECT_ROOT, "results");
const STEM_RE = /^[a-zA-Z0-9_-]+$/;
const RUN_RE = /^[a-zA-Z0-9._-]+$/;
const PRED_FILE_RE =
  /^(?<stem>[a-zA-Z0-9_-]+)\.mask\.(?<attempt>\d+)\.pred\.png$/;

const RUN_INCLUDE_TOKEN = "-150";
const PREFERRED_RUN = "gemini-pro-150";

const listRuns = async (dataset: DatasetId): Promise<string[]> => {
  const config = DATASETS[dataset];
  const resultsDir = path.join(RESULTS_ROOT, config.resultsSubDir);
  try {
    const entries = await fs.readdir(resultsDir, { withFileTypes: true });
    return entries
      .filter(
        (entry) =>
          entry.isDirectory() && entry.name.includes(RUN_INCLUDE_TOKEN),
      )
      .map((entry) => entry.name)
      .sort((a, b) => a.localeCompare(b));
  } catch (error) {
    if (
      typeof error === "object" &&
      error !== null &&
      "code" in error &&
      (error as { code?: string }).code === "ENOENT"
    ) {
      return [];
    }
    throw error;
  }
};

const buildFileUrl = (
  dataset: DatasetId,
  stem: string,
  kind: "img" | "ref" | "pred",
  run?: string,
  attempt?: number,
): string => {
  const params = new URLSearchParams({
    dataset,
    stem,
    kind,
  });
  if (run) params.set("run", run);
  if (attempt !== undefined) params.set("attempt", String(attempt));
  return `/api/file?${params.toString()}`;
};

export async function GET(request: Request): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(request.url);
    const datasetParam = searchParams.get("dataset");
    const runParam = searchParams.get("run");
    const dataset = isDatasetId(datasetParam) ? datasetParam : DEFAULT_DATASET;

    const runs = await listRuns(dataset);
    if (!runs.length) {
      const body: SamplesResponse = {
        dataset,
        run: null,
        runs,
        samples: [],
      };
      return NextResponse.json(body);
    }

    const requestedRun =
      runParam && RUN_RE.test(runParam) && runs.includes(runParam)
        ? runParam
        : runs.includes(PREFERRED_RUN)
          ? PREFERRED_RUN
          : runs[0];
    const runDir = path.join(
      RESULTS_ROOT,
      DATASETS[dataset].resultsSubDir,
      requestedRun,
    );

    const entries = await fs.readdir(runDir, { withFileTypes: true });
    const sampleAttempts = new Map<string, Set<number>>();

    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const match = entry.name.match(PRED_FILE_RE);
      if (!match?.groups) continue;
      const { stem, attempt } = match.groups;
      if (!STEM_RE.test(stem)) continue;
      const attemptIndex = Number.parseInt(attempt, 10);
      if (Number.isNaN(attemptIndex)) continue;
      let attempts = sampleAttempts.get(stem);
      if (!attempts) {
        attempts = new Set();
        sampleAttempts.set(stem, attempts);
      }
      attempts.add(attemptIndex);
    }

    const samples: Sample[] = Array.from(sampleAttempts.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([stem, attempts]) => {
        const sortedAttempts = Array.from(attempts).sort((a, b) => a - b);
        return {
          stem,
          imageUrl: buildFileUrl(dataset, stem, "img"),
          refUrl: buildFileUrl(dataset, stem, "ref"),
          predUrls: sortedAttempts.map((attempt) =>
            buildFileUrl(dataset, stem, "pred", requestedRun, attempt),
          ),
        };
      });

    const body: SamplesResponse = {
      dataset,
      run: requestedRun,
      runs,
      samples,
    };

    return NextResponse.json(body);
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
