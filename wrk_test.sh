#!/bin/bash

# ================================
# wrk 壓測腳本 (並行執行)
# 可透過參數指定執行時間 (-d)
# ================================

BENCHMARKS=(
  "Golang Gin|http://gin:8080/ping"
  "Java Spring Boot|http://springboot:8080/ping"
  "Java Quarkus|http://quarkus:8080/ping"
)

# 初始檢查所有服務是否可用
echo ""
echo "=== Checking service availability ==="
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    url="${entry##*|}"

    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")
    if [ "$status_code" != "200" ]; then
        echo " - $name ($url) is not available (status: $status_code)"
        echo " - Please make sure the service is started before performing stress testing."
        exit 1
    else
        echo " - $name ($url) is available (status: $status_code)"
    fi
done
echo ""

MODE=${1:-baseline}

case "$MODE" in
  short) THREADS=2; CONNECTIONS=100; DURATION=15s ;;
  baseline) THREADS=4; CONNECTIONS=200; DURATION=300s ;;
  normal) THREADS=8; CONNECTIONS=1000; DURATION=900s ;;
  stress) THREADS=8; CONNECTIONS=2500; DURATION=1800s ;;
  extreme) THREADS=8; CONNECTIONS=5000; DURATION=3600s ;;
  *) echo "Unknown mode: $MODE"; echo "Usage: $0 {baseline|normal|stress|extreme}"; exit 1 ;;
esac

echo "=== All benchmarks start === $(date +"%Y-%m-%d %H:%M:%S")"
echo "Perform stress testing according to the following settings:"
printf " - mode: $MODE\n - threads: $THREADS\n - connections: $CONNECTIONS\n - duration: $DURATION\n\n"

LOG_DIR="./benchmark_log"
mkdir -p "$LOG_DIR"
OUTPUT_LOG="$LOG_DIR/wrk_results.log"
echo "" > "$OUTPUT_LOG"

function show_progress_bar() {
    local duration=$1
    local seconds=$(( ${duration%s} ))
    echo "Benchmark Progress:"
    for ((i=0; i<=seconds; i++)); do
        percent=$(( i * 100 / seconds ))
        done_blocks=$(( percent / 3 ))
        pending_blocks=$(( 33 - done_blocks ))

        bar=""
        for ((j=0; j<done_blocks; j++)); do bar="${bar}#"; done
        for ((j=0; j<pending_blocks; j++)); do bar="${bar}-"; done

        printf "\r[%s] %3d%%  Elapsed: %02d:%02d:%02d" "$bar" "$percent" $((i/3600)) $(( (i%3600)/60 )) $((i%60))
        sleep 1
    done
    echo ""
}

function wait_for_service() {
    local url=$1
    local name=$2
    local retries=20
    local wait=3

    for i in $(seq 1 $retries); do
        status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" || echo "000")
        if [ "$status_code" = "200" ]; then
            return 0
        fi
        sleep $wait
    done
    return 1
}

function run_benchmark() {
    local name=$1
    local url=$2
    local logfile="$LOG_DIR/${name// /_}.log"

    echo "=== $name ===" > "$logfile"

    wait_for_service "$url" "$name" >> "$logfile" 2>&1
    if [ $? -ne 0 ]; then
        echo "[ERROR] $name not ready. Skipping benchmark." | tee -a "$logfile"
        return
    fi

    wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} -s wrk/benchmark.lua "$url" >> "$logfile" 2>&1 &
}

echo "Currently executed benchmarks: "
for i in "${!BENCHMARKS[@]}"; do
    name="${BENCHMARKS[$i]%%|*}"
    echo -n " - $name"
    if [ $i -lt $((${#BENCHMARKS[@]} - 1)) ]; then echo -n ","; fi
done
echo -e "\n"

# 執行 benchmark
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    url="${entry##*|}"
    run_benchmark "$name" "$url"
done

# 顯示進度條
show_progress_bar ${DURATION%s} &

wait

# 合併 log
> "$OUTPUT_LOG"
for entry in "${BENCHMARKS[@]}"; do
    name="${entry%%|*}"
    logfile="$LOG_DIR/${name// /_}.log"
    if [ -f "$logfile" ]; then
        echo "=== Log for $name ===" >> "$OUTPUT_LOG"
        cat "$logfile" >> "$OUTPUT_LOG"
        echo "" >> "$OUTPUT_LOG"
    fi
done

echo "=== All benchmarks completed === $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$OUTPUT_LOG"
echo ""
