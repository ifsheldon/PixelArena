"use client";

import Image from "next/image";
import type { MouseEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DATASET_OPTIONS,
  type DatasetId,
  DEFAULT_DATASET,
  getDatasetLabel,
} from "@/lib/datasets";
import { getDatasetLabels, getLabelByRGB } from "@/lib/labels";

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

export default function Home() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [idx, setIdx] = useState(0);
  const [infoText, setInfoText] = useState<string>("");
  const [selectedDataset, setSelectedDataset] =
    useState<DatasetId>(DEFAULT_DATASET);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [activeDataset, setActiveDataset] =
    useState<DatasetId>(DEFAULT_DATASET);
  const [activeRun, setActiveRun] = useState<string | null>(null);
  const [availableRuns, setAvailableRuns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    const loadSamples = async () => {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({ dataset: selectedDataset });
      if (selectedRun) params.set("run", selectedRun);
      try {
        const response = await fetch(`/api/samples?${params.toString()}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Failed to load samples (${response.status})`);
        }
        const data: SamplesResponse = await response.json();
        if (cancelled) return;
        setSamples(data.samples ?? []);
        setAvailableRuns(data.runs ?? []);
        setActiveRun(data.run ?? null);
        setActiveDataset(data.dataset);
        setIdx(0);
        setInfoText("");
        if (
          selectedRun &&
          data.run &&
          selectedRun !== data.run &&
          data.runs?.includes(data.run)
        ) {
          setSelectedRun(data.run);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setSamples([]);
        setAvailableRuns([]);
        setActiveRun(null);
        setError(err instanceof Error ? err.message : "Failed to load samples");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadSamples();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [selectedDataset, selectedRun]);

  const current = samples[idx] as Sample | undefined;
  const datasetName = getDatasetLabel(activeDataset);
  const labelList = useMemo(
    () => getDatasetLabels(activeDataset),
    [activeDataset],
  );
  const labelSummary =
    labelList.length <= 40
      ? labelList.join(", ")
      : `${labelList.slice(0, 40).join(", ")}, …`;
  const headingParts = [
    datasetName,
    activeRun ?? undefined,
    current?.stem ?? undefined,
  ].filter(Boolean);
  const title = headingParts.join(" · ") || "No data";

  const onKey = useCallback(
    (e: KeyboardEvent) => {
      if (!samples.length) return;
      if (e.key === "ArrowRight") {
        setIdx((v) => (v + 1) % samples.length);
      } else if (e.key === "ArrowLeft") {
        setIdx((v) => (v - 1 + samples.length) % samples.length);
      }
    },
    [samples.length],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onKey]);

  const handleClickMask = useCallback(
    async (evt: MouseEvent<HTMLImageElement>, sample: Sample) => {
      const img = evt.currentTarget;
      const rect = img.getBoundingClientRect();
      const x = Math.floor(
        ((evt.clientX - rect.left) / rect.width) * img.naturalWidth,
      );
      const y = Math.floor(
        ((evt.clientY - rect.top) / rect.height) * img.naturalHeight,
      );

      const fetchLabelAt = async (url?: string) => {
        if (!url) return "n/a";
        try {
          const response = await fetch(url, { cache: "force-cache" });
          if (!response.ok) {
            return "error";
          }
          const blob = await response.blob();
          const bitmap = await createImageBitmap(blob);
          const canvas = document.createElement("canvas");
          canvas.width = bitmap.width;
          canvas.height = bitmap.height;
          const ctx = canvas.getContext("2d");
          if (!ctx) {
            bitmap.close();
            return "error";
          }
          ctx.drawImage(bitmap, 0, 0);
          const sampleX = Math.min(Math.max(x, 0), bitmap.width - 1);
          const sampleY = Math.min(Math.max(y, 0), bitmap.height - 1);
          const data = ctx.getImageData(sampleX, sampleY, 1, 1).data;
          bitmap.close();
          const match = getLabelByRGB(activeDataset, data[0], data[1], data[2]);
          return match ? `${match.index}: ${match.name}` : "unknown";
        } catch (error) {
          console.error("Failed to sample label", error);
          return "error";
        }
      };
      const labelEntries = [
        ["Ref", await fetchLabelAt(sample.refUrl)],
        ...(await Promise.all(
          (sample.predUrls ?? []).map(async (url, i) => [
            `P${i}`,
            await fetchLabelAt(url),
          ]),
        )),
      ];

      setInfoText(
        `(${x}, ${y}) → ${labelEntries
          .map(([tag, value]) => `${tag}: ${value}`)
          .join(" | ")}`,
      );
    },
    [activeDataset],
  );

  const handleDatasetChange = (dataset: DatasetId) => {
    if (dataset === selectedDataset) return;
    setSelectedDataset(dataset);
    setSelectedRun(null);
    setAvailableRuns([]);
    setActiveRun(null);
    setSamples([]);
    setInfoText("");
    setError(null);
    setIdx(0);
  };

  const handleRunChange = (runValue: string) => {
    setSelectedRun(runValue || null);
    setIdx(0);
    setInfoText("");
  };

  return (
    <div className="min-h-screen p-6 flex flex-col items-center justify-center gap-6">
      <h1 className="text-xl font-semibold text-center">{title}</h1>

      <div className="flex flex-wrap items-end justify-center gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase tracking-wide text-gray-500">
            Dataset
          </span>
          <select
            className="border rounded px-3 py-1"
            value={selectedDataset}
            onChange={(event) =>
              handleDatasetChange(event.target.value as DatasetId)
            }
          >
            {DATASET_OPTIONS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase tracking-wide text-gray-500">
            Run
          </span>
          <select
            className="border rounded px-3 py-1"
            value={selectedRun ?? activeRun ?? ""}
            onChange={(event) => handleRunChange(event.target.value)}
            disabled={!availableRuns.length}
          >
            {availableRuns.length ? (
              availableRuns.map((run) => (
                <option key={run} value={run}>
                  {run}
                </option>
              ))
            ) : (
              <option value="">
                {loading ? "Loading runs..." : "No runs found"}
              </option>
            )}
          </select>
        </label>

        <div className="text-sm text-gray-500 min-w-[10rem] text-center">
          {loading ? "Loading samples…" : `${samples.length} samples`}
        </div>
      </div>

      {error ? (
        <div className="text-sm text-red-500 text-center">{error}</div>
      ) : null}

      {current ? (
        <div className="flex flex-col gap-6">
          {/* Top Row: Image and Reference */}
          <div className="flex flex-row gap-4 justify-center">
            <figure className="flex flex-col gap-2 items-center">
              {current.imageUrl ? (
                <Image
                  src={current.imageUrl}
                  alt="input"
                  className="max-w-[30vw] h-auto rounded border"
                  width={512}
                  height={512}
                  draggable={false}
                  unoptimized
                />
              ) : (
                <div className="w-[30vw] aspect-square border rounded grid place-items-center text-gray-500">
                  No image
                </div>
              )}
              <figcaption className="text-sm text-gray-500">Image</figcaption>
            </figure>

            <figure className="flex flex-col gap-2 items-center">
              {current.refUrl ? (
                <Image
                  src={current.refUrl}
                  alt="reference mask"
                  className="max-w-[30vw] h-auto rounded border cursor-crosshair"
                  onClick={(e) => handleClickMask(e, current)}
                  role="img"
                  width={512}
                  height={512}
                  draggable={false}
                  unoptimized
                />
              ) : (
                <div className="w-[30vw] aspect-square border rounded grid place-items-center text-gray-500">
                  No reference
                </div>
              )}
              <figcaption className="text-sm text-gray-500">
                Reference
              </figcaption>
            </figure>
          </div>

          {/* Bottom Row: Predictions */}
          <div className="flex flex-row gap-4 justify-center flex-wrap">
            {(current.predUrls ?? []).length ? (
              current.predUrls.map((url, i) => (
                <figure
                  key={`${current.stem}-pred-${i}`}
                  className="flex flex-col gap-2 items-center"
                >
                  <Image
                    src={url}
                    alt={`prediction mask ${i}`}
                    className="max-w-[20vw] h-auto rounded border cursor-crosshair"
                    onClick={(e) => handleClickMask(e, current)}
                    role="img"
                    width={512}
                    height={512}
                    draggable={false}
                    unoptimized
                  />
                  <figcaption className="text-sm text-gray-500">
                    Prediction {i}
                  </figcaption>
                </figure>
              ))
            ) : (
              <div className="text-gray-500 text-sm">No predictions found.</div>
            )}
          </div>

          <div className="text-sm text-center">
            Click on any mask to inspect classes across all masks at that
            coordinate. <br />
            {infoText}
          </div>
        </div>
      ) : (
        <div className="text-gray-500">No samples found.</div>
      )}

      <div className="text-xs text-gray-500 text-center">
        Use ← and → to navigate
      </div>
      <div className="text-xs text-gray-500 text-center">
        Classes ({labelList.length}): {labelSummary}
      </div>
    </div>
  );
}
