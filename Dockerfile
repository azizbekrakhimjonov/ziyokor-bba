# Linux server uchun ishonchli build (better-sqlite3 native modul shu yerda yig‘iladi).
FROM node:22-bookworm-slim AS build
RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 make g++ \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json bun.lock ./
RUN npm install
COPY . .
RUN npm run build

FROM node:22-bookworm-slim
RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 make g++ \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app/.output ./.output
COPY scripts/start-server.sh ./scripts/start-server.sh
RUN chmod +x ./scripts/start-server.sh
ENV HOST=0.0.0.0
ENV PORT=8080
ENV BBA_SQLITE_PATH=/app/data/bba.sqlite
VOLUME ["/app/data"]
EXPOSE 8080
CMD ["sh", "./scripts/start-server.sh"]
