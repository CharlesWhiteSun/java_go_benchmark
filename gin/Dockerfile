# build stage
FROM golang:1.24 AS build

WORKDIR /app

COPY . .

RUN go mod init gin-benchmark \
    && go get github.com/gin-gonic/gin \
    && go build -o app .

FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/app .

CMD ["./app"]
