"use client";

import { useSearchParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import type { MouseEvent } from "react";
import { useCallback, useEffect, useMemo, useState, Suspense } from "react";
import {
  DATASET_OPTIONS,
  type DatasetId,
  DEFAULT_DATASET,
  getDatasetLabel,
  isDatasetId,
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

function CompareContent() {
  const searchParams = useSearchParams();
  const [samples, setSamples] = useState<Sample[]>([]);
  const [idx, setIdx] = useState(0);
  const [infoText, setInfoText] = useState<string>("");
  const [pixelLabels, setPixelLabels] = useState<Record<string, string>>({});
  const [selectedDataset, setSelectedDataset] = useState<DatasetId>(() => {
    const ds = searchParams.get("dataset");
    return isDatasetId(ds) ? ds : DEFAULT_DATASET;
  });
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [activeDataset, setActiveDataset] =
    useState<DatasetId>(DEFAULT_DATASET);
  const [activeRun, setActiveRun] = useState<string | null>(null);
  const [availableRuns, setAvailableRuns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
        
        // Handle stem parameter
        const stemParam = searchParams.get("stem");
        if (stemParam) {
           const foundIdx = (data.samples ?? []).findIndex(s => s.stem === stemParam);
           if (foundIdx !== -1) {
             setIdx(foundIdx);
           } else {
             setIdx(0);
           }
        } else {
           setIdx(0);
        }

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

      const newPixelLabels: Record<string, string> = {
        ref: await fetchLabelAt(sample.refUrl),
      };

      await Promise.all(
        (sample.predUrls ?? []).map(async (url, i) => {
          newPixelLabels[`pred-${i}`] = await fetchLabelAt(url);
        }),
      );

      setPixelLabels(newPixelLabels);
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
    setPixelLabels({});
    setError(null);
    setIdx(0);
  };

  const handleRunChange = (runValue: string) => {
    setSelectedRun(runValue || null);
    setIdx(0);
    setInfoText("");
    setPixelLabels({});
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex flex-wrap items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
        <h1 className="text-xl font-bold">PixelArena</h1>

        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <span className="text-gray-500 font-medium">Dataset:</span>
            <select
              className="border rounded px-2 py-1"
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

          <label className="flex items-center gap-2 text-sm">
            <span className="text-gray-500 font-medium">Run:</span>
            <select
              className="border rounded px-2 py-1"
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
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center p-4 gap-4">
        {error ? (
          <div className="text-sm text-red-500 text-center">{error}</div>
        ) : null}

        {current ? (
        <div className="flex flex-col gap-4">
          <div className="text-xs text-gray-500 text-center leading-tight">
            <div>Use ← and → to navigate</div>
            <div>
              Click on any mask to inspect classes across all masks at that
              coordinate.
            </div>
          </div>

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
              <figcaption className="text-sm text-gray-500">
                Image
                <div className="text-xs font-mono text-black mt-1">
                  id = {current.stem}
                </div>
              </figcaption>
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
                {pixelLabels.ref && (
                  <div className="text-xs font-mono text-black mt-1">
                    {pixelLabels.ref}
                  </div>
                )}
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
                    {pixelLabels[`pred-${i}`] && (
                      <div className="text-xs font-mono text-black mt-1">
                        {pixelLabels[`pred-${i}`]}
                      </div>
                    )}
                  </figcaption>
                </figure>
              ))
            ) : (
              <div className="text-gray-500 text-sm">No predictions found.</div>
            )}
          </div>

          <div className="text-sm text-center">
            {infoText}
          </div>
        </div>
      ) : (
        <div className="text-gray-500">No samples found.</div>
      )}

      <div className="w-full max-w-4xl text-xs text-gray-500">
          <h3 className="text-center mb-2">Classes ({labelList.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 text-left p-4 border rounded bg-gray-50">
            {labelList.map((label, i) => (
              <div key={label} className="truncate" title={label}>
                <span className="font-mono text-gray-400 mr-1">{i}:</span>
                {label}
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Floating Action Button (Right - Image List) */}
      <div className="fixed bottom-6 right-6 z-50 group flex items-center gap-2">
        <span className="bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-md pointer-events-none">
          Image List
        </span>
        <button
          onClick={() => setIsMenuOpen(true)}
          className="p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
          aria-label="Open sample list"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-5 h-5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
          </svg>
        </button>
      </div>

      {/* Floating Action Button (Left - Back to Gallery) */}
      <div className="fixed bottom-6 left-6 z-50 group flex items-center gap-2 flex-row-reverse">
        <span className="bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-md pointer-events-none">
          Back to Gallery
        </span>
        <Link
          href={`/?dataset=${selectedDataset}`}
          className="p-3 bg-gray-600 text-white rounded-full shadow-lg hover:bg-gray-700 transition-colors flex items-center justify-center"
          aria-label="Back to Gallery"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-5 h-5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
            />
          </svg>
        </Link>
      </div>

      {/* Slide-over Menu */}
      <div
        className={`fixed inset-0 z-50 transition-opacity duration-300 ${
          isMenuOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/50"
          onClick={() => setIsMenuOpen(false)}
        />

        {/* Panel */}
        <div
          className={`absolute right-0 top-0 bottom-0 w-80 bg-white shadow-xl transform transition-transform duration-300 flex flex-col ${
            isMenuOpen ? "translate-x-0" : "translate-x-full"
          }`}
        >
          <div className="p-4 border-b flex items-center justify-between bg-gray-50">
            <h2 className="font-semibold text-lg">{datasetName} ({samples.length})</h2>
            <button
              onClick={() => setIsMenuOpen(false)}
              className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              aria-label="Close menu"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {samples.length > 0 ? (
              <ul className="space-y-1">
                {samples.map((sample, i) => (
                  <li key={sample.stem}>
                    <button
                      onClick={() => {
                        setIdx(i);
                        setIsMenuOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm rounded transition-colors ${
                        i === idx
                          ? "bg-blue-100 text-blue-800 font-medium"
                          : "hover:bg-gray-100 text-gray-700"
                      }`}
                    >
                      {i + 1}. {sample.stem}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-4 text-center text-gray-500 text-sm">
                No samples loaded
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Compare() {
  return (
    <Suspense>
      <CompareContent />
    </Suspense>
  );
}

