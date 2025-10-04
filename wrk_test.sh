#!/bin/bash

# ================================
# wrk 壓測腳本 (並行執行)
# 可透過參數指定執行時間 (-d)
# ================================

# Benchmark 名稱與對應 URL 陣列
BENCHMARKS=(
  "Golang Gin|http://localhost:8083/ping"
  "Java Spring Boot|http://localhost:8081/ping"
  "Java Quarkus|http://localhost:8082/ping"
)

# 先檢查所有服務是否可連線
echo ""
echo "=== Checking service availability ==="
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    url="${entry##*|}"

    # 用 curl 測試是否能連線成功
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")

    if [ "$status_code" != "200" ]; then
        echo " - $name ($url) is not available (status: $status_code)"
        echo " - Please make sure the service is started (for example, Docker Desktop is open) before performing stress testing."
        exit 1
    else
        echo " - $name ($url) is available (status: $status_code)"
    fi
done
echo ""

MODE=${1:-baseline}   # 預設 baseline

case "$MODE" in
  baseline)
    THREADS=4
    CONNECTIONS=200
    DURATION=300s
    ;;
  normal)
    THREADS=8
    CONNECTIONS=1000
    DURATION=900s
    ;;
  stress)
    THREADS=8
    CONNECTIONS=2500
    DURATION=1800s
    ;;
  extreme)
    THREADS=8
    CONNECTIONS=5000
    DURATION=3600s
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Usage: $0 {baseline|normal|stress|extreme}"
    exit 1
    ;;
esac

echo "=== All benchmarks start === $(date +"%Y-%m-%d %H:%M:%S")"
echo "Perform stress testing according to the following settings:"
printf " - mode: $MODE"
printf "\n - threads: $THREADS"
printf "\n - connections: $CONNECTIONS"
printf "\n - duration: $DURATION"
echo ""
echo ""

LOG_DIR="./benchmark_log"
mkdir -p "$LOG_DIR"
OUTPUT_LOG="$LOG_DIR/wrk_results.log"
echo "" > "$OUTPUT_LOG"

function run_benchmark() {
    local name=$1
    local url=$2
    local logfile="$LOG_DIR/${name// /_}.log"

    echo "=== $name ===" > "$logfile"
    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} -s wrk/benchmark.lua "$url" >> "$logfile" 2>&1 &
}

function show_progress_bar() {
    local duration=$1
    local seconds=$(( ${duration%s} ))

    echo "Benchmark Progress:"
    for ((i=0; i<=seconds; i++)); do
        percent=$(( i * 100 / seconds ))
        done_blocks=$(( percent / 3 )) # 讓進度條更長
        pending_blocks=$(( 33 - done_blocks ))

        bar=""
        for ((j=0; j<done_blocks; j++)); do bar="${bar}#"; done
        for ((j=0; j<pending_blocks; j++)); do bar="${bar}-"; done

        printf "\r[%s] %3d%%  Elapsed: %02d:%02d:%02d" "$bar" "$percent" $((i/3600)) $(( (i%3600)/60 )) $((i%60))
        sleep 1
    done
    echo ""
}



echo "Currently executed benchmarks: "
printf " - "
for i in "${!BENCHMARKS[@]}"; do
    name="${BENCHMARKS[$i]%%|*}"
    echo -n "$name"
    if [ $i -lt $((${#BENCHMARKS[@]} - 1)) ]; then
        echo -n ", "
    fi
done
echo ""
echo ""

# 執行 benchmark
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    url="${entry##*|}"
    run_benchmark "$name" "$url"
done

# 顯示單一進度條
show_progress_bar "$DURATION" &

wait

# 合併 log
> "$OUTPUT_LOG"
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    logfile="$LOG_DIR/${name// /_}.log"
    cat "$logfile" >> "$OUTPUT_LOG"
done

echo "=== All benchmarks completed === $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$OUTPUT_LOG"
echo ""
