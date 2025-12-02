import { promises as fs } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";

function resolvePath(
  stem: string,
  kind: string,
): { abs: string; contentType: string } | undefined {
  const testResultDir = path.resolve(process.cwd(), "../test");
  const evalSetDir = path.resolve(process.cwd(), "../eval-set/celeb");

  if (!/^[a-zA-Z0-9_-]+$/.test(stem)) return undefined;
  switch (kind) {
    case "img":
      return {
        abs: path.join(testResultDir, `${stem}.jpg`),
        contentType: "image/jpeg",
      };
    case "ref":
      return {
        abs: path.join(evalSetDir, `masks-1024/${stem}.png`),
        contentType: "image/png",
      };
    case "pred0":
      return {
        abs: path.join(testResultDir, `${stem}.mask.0.pred.png`),
        contentType: "image/png",
      };
    case "pred1":
      return {
        abs: path.join(testResultDir, `${stem}.mask.1.pred.png`),
        contentType: "image/png",
      };
    case "pred2":
      return {
        abs: path.join(testResultDir, `${stem}.mask.2.pred.png`),
        contentType: "image/png",
      };
    default:
      return undefined;
  }
}

export async function GET(request: Request): Promise<NextResponse> {
  const { searchParams } = new URL(request.url);
  const stem = searchParams.get("stem");
  const kind = searchParams.get("kind");
  if (!stem || !kind) {
    return NextResponse.json(
      { error: "Missing stem or kind" },
      { status: 400 },
    );
  }
  const resolved = resolvePath(stem, kind);
  if (!resolved) {
    return NextResponse.json({ error: "Invalid parameters" }, { status: 400 });
  }
  try {
    const buffer = await fs.readFile(resolved.abs);
    const arrayBuffer = new ArrayBuffer(buffer.byteLength);
    new Uint8Array(arrayBuffer).set(buffer);
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
