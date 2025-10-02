# build stage
FROM golang:1.24 AS build

WORKDIR /app

COPY . .

RUN go mod init gin-benchmark \
    && go get github.com/gin-gonic/gin \
    && go build -o app .

# runtime stage
FROM gcr.io/distroless/base-debian12

WORKDIR /app

COPY --from=build /app/app .

CMD ["./app"]
