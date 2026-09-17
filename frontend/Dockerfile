FROM oven/bun:1.4.2 AS bun

FROM node:24-bookworm-slim AS builder
WORKDIR /app/frontend

COPY --from=bun /usr/local/bin/bun /usr/local/bin/bun
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_OUTPUT_STANDALONE=1
RUN bun run build

FROM node:24-bookworm-slim AS runner
WORKDIR /app/frontend

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3011

COPY --from=builder --chown=node:node /app/frontend/.next/standalone ./
COPY --from=builder --chown=node:node /app/frontend/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/frontend/public ./public

USER node
EXPOSE 3011
CMD ["node", "server.js"]
