import { promises as fs } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";

type Sample = {
  stem: string;
  imageUrl?: string;
  predUrl?: string;
  refUrl?: string;
};

export async function GET(): Promise<NextResponse> {
  try {
    // Use absolute path to project root data/val_preds
    const baseDir = path.resolve(
      "/Users/zhiqiu/offline_code/research_ntu/cv-is-dead/test-masks",
    );
    const entries = await fs.readdir(baseDir, { withFileTypes: true });

    const jpgStems = new Set<string>();
    const refPngStems = new Set<string>();
    const predPngStems = new Set<string>();

    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const name = entry.name;
      if (name.endsWith(".jpg")) {
        jpgStems.add(name.slice(0, -".jpg".length));
      } else if (name.endsWith(".pred.png")) {
        predPngStems.add(name.slice(0, -".pred.png".length));
      } else if (name.endsWith(".png")) {
        // Reference mask (exclude .pred.png which handled above)
        refPngStems.add(name.slice(0, -".png".length));
      }
    }

    const stems = new Set<string>([...jpgStems, ...refPngStems, ...predPngStems]);
    const sorted = Array.from(stems).sort();

    const samples: Sample[] = sorted.map((stem) => {
      const imageUrl = jpgStems.has(stem)
        ? `/api/file?stem=${encodeURIComponent(stem)}&kind=img`
        : undefined;
      const predUrl = predPngStems.has(stem)
        ? `/api/file?stem=${encodeURIComponent(stem)}&kind=pred`
        : undefined;
      const refUrl = refPngStems.has(stem)
        ? `/api/file?stem=${encodeURIComponent(stem)}&kind=ref`
        : undefined;
      return { stem, imageUrl, predUrl, refUrl } satisfies Sample;
    });

    return NextResponse.json({ samples });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
