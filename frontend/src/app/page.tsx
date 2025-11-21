"use client";

import Image from "next/image";
import type { MouseEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { getLabelByRGB, LABELS } from "@/lib/labels";

type Sample = {
  stem: string;
  imageUrl?: string;
  refUrl?: string;
  pred0Url?: string;
  pred1Url?: string;
  pred2Url?: string;
};

export default function Home() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [idx, setIdx] = useState(0);
  const [infoText, setInfoText] = useState<string>("");

  useEffect(() => {
    fetch("/api/samples")
      .then((r) => r.json())
      .then((d) => setSamples(d.samples ?? []))
      .catch(() => setSamples([]));
  }, []);

  const current = samples[idx] as Sample | undefined;

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
          const match = getLabelByRGB(data[0], data[1], data[2]);
          return match ? `${match.index}: ${match.name}` : "unknown";
        } catch (error) {
          console.error("Failed to sample label", error);
          return "error";
        }
      };

      // We might want to show what was clicked specifically or all of them.
      // The original code fetched both pred and ref.
      // Now we have 3 preds. Fetching all 5 labels (including image?) might be slow/overkill but useful.
      // Let's fetch Reference + Preds.
      
      const [refLabel, p0Label, p1Label, p2Label] = await Promise.all([
        fetchLabelAt(sample.refUrl),
        fetchLabelAt(sample.pred0Url),
        fetchLabelAt(sample.pred1Url),
        fetchLabelAt(sample.pred2Url),
      ]);

      setInfoText(`(${x}, ${y}) → Ref: ${refLabel} | P0: ${p0Label} | P1: ${p1Label} | P2: ${p2Label}`);
    },
    [],
  );

  const title = useMemo(() => current?.stem ?? "No data", [current]);

  return (
    <div className="min-h-screen p-6 flex flex-col items-center justify-center gap-6">
      <h1 className="text-xl font-semibold text-center">{title}</h1>
      
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
              <figcaption className="text-sm text-gray-500">Reference</figcaption>
            </figure>
          </div>

          {/* Bottom Row: Predictions */}
          <div className="flex flex-row gap-4 justify-center">
             {[current.pred0Url, current.pred1Url, current.pred2Url].map((url, i) => (
               <figure key={i} className="flex flex-col gap-2 items-center">
                 {url ? (
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
                 ) : (
                   <div className="w-[20vw] aspect-square border rounded grid place-items-center text-gray-500">
                     No pred {i}
                   </div>
                 )}
                 <figcaption className="text-sm text-gray-500">Prediction {i}</figcaption>
               </figure>
             ))}
          </div>

          <div className="text-sm text-center">
            Click on any mask to inspect classes across all masks at that coordinate. <br />
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
        Classes: {LABELS.join(", ")}
      </div>
    </div>
  );
}
