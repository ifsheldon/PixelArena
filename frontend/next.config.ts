import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker uses the standalone server; local builds keep supporting next start.
  output: process.env.NEXT_OUTPUT_STANDALONE === "1" ? "standalone" : undefined,
};

export default nextConfig;
