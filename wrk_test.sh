#!/bin/bash

# ================================
# wrk 壓測腳本
# 可透過參數指定 threads (-t)、connections (-c)、duration (-d)
# ================================

# 預設參數
THREADS=${1:-12}     # -t : threads，wrk 使用的執行緒數量
CONNECTIONS=${2:-400} # -c : connections，wrk 建立的同時連線數
DURATION=${3:-1m}    # -d : duration，測試持續時間 (如 30s、1m)

# log 目錄與檔案
LOG_DIR="./log"
mkdir -p $LOG_DIR
OUTPUT_LOG="$LOG_DIR/wrk_results.log"
echo "" > $OUTPUT_LOG

echo "=== Gin Benchmark ===" | tee -a $OUTPUT_LOG
wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} -s wrk/benchmark.lua http://localhost:8083/ping | tee -a $OUTPUT_LOG

echo "=== Spring Boot Benchmark ===" | tee -a $OUTPUT_LOG
wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} -s wrk/benchmark.lua http://localhost:8081/ping | tee -a $OUTPUT_LOG

echo "=== Quarkus Benchmark ===" | tee -a $OUTPUT_LOG
wrk -t${THREADS} -c${CONNECTIONS} -d${DURATION} -s wrk/benchmark.lua http://localhost:8082/ping | tee -a $OUTPUT_LOG

echo "=== All benchmarks completed ===" | tee -a $OUTPUT_LOG
