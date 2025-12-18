"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  DATASET_OPTIONS,
  type DatasetId,
  DEFAULT_DATASET,
} from "@/lib/datasets";

type ImageItem = {
  stem: string;
  url: string;
};

type ImagesResponse = {
  dataset: DatasetId;
  images: ImageItem[];
};

const BATCH_SIZE = 50;

export default function Gallery() {
  const [dataset, setDataset] = useState<DatasetId>(DEFAULT_DATASET);
  const [allImages, setAllImages] = useState<ImageItem[]>([]);
  const [visibleCount, setVisibleCount] = useState(BATCH_SIZE);
  const [_loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const observerTarget = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();

    const loadImages = async () => {
      setLoading(true);
      setError(null);
      setAllImages([]);
      setVisibleCount(BATCH_SIZE);

      try {
        const response = await fetch(`/api/images?dataset=${dataset}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Failed to load images (${response.status})`);
        }
        const data: ImagesResponse = await response.json();
        if (cancelled) return;
        setAllImages(data.images);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load images");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadImages();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [dataset]);

  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [target] = entries;
    if (target.isIntersecting) {
      setVisibleCount((prev) => prev + BATCH_SIZE);
    }
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: Re-attach if list changes, as the observer target might be conditionally rendered
  useEffect(() => {
    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: "200px",
      threshold: 0,
    });

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => observer.disconnect();
  }, [handleObserver, allImages]);

  const visibleImages = allImages.slice(0, visibleCount);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
        <h1 className="text-xl font-bold">PixelArena Gallery</h1>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Dataset
            </span>
            <select
              className="bg-transparent border-none text-sm font-medium text-gray-900 focus:ring-0 cursor-pointer py-1 outline-none"
              value={dataset}
              onChange={(e) => setDataset(e.target.value as DatasetId)}
            >
              {DATASET_OPTIONS.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <Link
            href={`/compare?dataset=${dataset}`}
            className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
          >
            Model Comparison
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
            >
              <title>Arrow icon</title>
              <path
                fillRule="evenodd"
                d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
                clipRule="evenodd"
              />
            </svg>
          </Link>
        </div>
      </header>

      <main className="flex-1 p-6">
        {error ? (
          <div className="text-sm text-red-500 text-center mb-6">{error}</div>
        ) : null}

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
          {visibleImages.map((img) => (
            <figure key={img.stem} className="flex flex-col gap-2">
              <Link
                href={`/compare?dataset=${dataset}&stem=${img.stem}`}
                className="block group"
              >
                <div className="aspect-square relative rounded overflow-hidden bg-gray-100 group-hover:ring-2 group-hover:ring-blue-500 transition-all">
                  <Image
                    src={img.url}
                    alt={img.stem}
                    fill
                    sizes="(max-width: 768px) 50vw, (max-width: 1024px) 25vw, 16vw"
                    className="object-cover transition-transform group-hover:scale-105"
                    loading="lazy"
                    unoptimized
                  />
                </div>
              </Link>
              <figcaption className="text-xs text-gray-500 text-center truncate font-mono">
                {img.stem}
              </figcaption>
            </figure>
          ))}
        </div>

        {visibleCount < allImages.length && (
          <div ref={observerTarget} className="h-10 w-full mt-8" />
        )}
      </main>
    </div>
  );
}
