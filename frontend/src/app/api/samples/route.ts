import { promises as fs } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";

type Sample = {
  stem: string;
  imageUrl?: string;
  refUrl?: string;
  pred0Url?: string;
  pred1Url?: string;
  pred2Url?: string;
};

export async function GET(): Promise<NextResponse> {
  try {
    // Use absolute path to project root test directory
    const testResultDir = path.resolve(process.cwd(), "../test");
    const entries = await fs.readdir(testResultDir, { withFileTypes: true });

    const stems = new Set<string>();

    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const name = entry.name;
      if (name.endsWith(".jpg") && !name.includes(".mask.")) {
        stems.add(name.slice(0, -".jpg".length));
      }
    }

    const sorted = Array.from(stems).sort();

    const samples: Sample[] = sorted.map((stem) => {
      const imageUrl = `/api/file?stem=${encodeURIComponent(stem)}&kind=img`;
      const refUrl = `/api/file?stem=${encodeURIComponent(stem)}&kind=ref`;
      const pred0Url = `/api/file?stem=${encodeURIComponent(stem)}&kind=pred0`;
      const pred1Url = `/api/file?stem=${encodeURIComponent(stem)}&kind=pred1`;
      const pred2Url = `/api/file?stem=${encodeURIComponent(stem)}&kind=pred2`;

      // We're not checking file existence for every variant here to save IO,
      // relying on file route to 404 if missing, or we could check.
      // Given the prompt implies existence, we can just provide URLs.
      // However, the original code checked existence.
      // Let's stick to providing URLs.

      return {
        stem,
        imageUrl,
        refUrl,
        pred0Url,
        pred1Url,
        pred2Url,
      } as any; // Casting to any because we need to update the Sample type definition but it is local
    });

    return NextResponse.json({ samples });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
