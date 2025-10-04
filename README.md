# Java & Go Benchmark Project

This repository contains a benchmarking project to compare the performance of different frameworks  
using **wrk** benchmark tests. The frameworks included are:

- **Gin** (Go)
- **Quarkus** (Java)
- **Spring Boot** (Java)

Benchmark results include metrics such as **Requests/sec**, **Average Latency (ms)**, and **Performance Efficiency**.


## 🚀 Setup & Build Instructions

This section explains step-by-step how to prepare, build, run,
and analyze the benchmarks for Gin, Quarkus, and Spring Boot.
Each command is shown in a code block, followed by its purpose.

1) Install WSL (Windows only):
Provides a Linux-like environment on Windows for running tools
like wrk and shell scripts without compatibility issues.
(Skip if you are already on Linux or macOS)
    ```bash
    wsl --install
    ```

2) Update package lists:
Ensures apt has the latest metadata and fetches current versions
of packages before installation.
    ```bash
    apt update
    ```

3) Install wrk:
wrk is a modern HTTP benchmarking tool used in this project
to generate load and measure throughput (Requests/sec) and
latency performance.
    ```bash
    apt install wrk
    ```

4) Build and run services with Docker Compose:
This builds Docker images for Gin, Quarkus, and Spring Boot,
then starts them in isolated containers with consistent configs.
    ```bash
    docker compose up -d --build
    ```

5) Change directory to the project working folder
Navigate to the project directory mounted in WSL or Linux
so that scripts (wrk_test.sh, wrk_analysis.py) can be executed.
Replace {disk} and {java project} with your actual path.
    ```bash
    cd /mnt/{disk}/{java project}/java_go_benchmark
    ```

6) Grant execute permission:
Make the benchmark script executable so it can be run directly.
    ```bash
    chmod +x wrk_test.sh
    ```

7) Run benchmark script:
Use the following command to run load tests with different configurations:
    ```bash
    sudo ./wrk_test.sh <mode>
    ```
    If no mode is specified, the script will default to the "baseline" mode.

    Modes and their parameters:
    
    | Mode     | Threads | Connections | Duration |
    | -------- | ------- | ----------- | -------- |
    | baseline | 4       | 200         | 300s     |
    | normal   | 8       | 1000        | 900s     |
    | stress   | 8       | 2500        | 1800s    |
    | extreme  | 8       | 5000        | 3600s    |

8) Install Python dependencies:
Install required Python libraries (e.g., matplotlib, pandas)
for analyzing and visualizing benchmark results.
    ```bash
    pip install -r requirements.txt
    ```

9) Run Python analysis script:
Generates summary tables and comparison charts (saved in charts/).
This step visualizes Requests/sec, Avg Latency, and Efficiency.
    ```bash
    python ./wrk_analysis.py
    ```


## 📄 Report

The benchmark analysis generates a detailed HTML report located at:
`benchmark_report/report.html`

This report includes:
- Summary table of all benchmarks
- Requests/sec comparison chart
- Average latency comparison chart
- Performance efficiency chart


## 📊 Benchmark Report & Charts

After running the benchmark and analysis, a detailed HTML report is generated along with charts stored in the `benchmark_charts/` directory.

You can preview these charts directly from this repository:

![Summary Table](charts/summary.png)

![Requests/sec Comparison](charts/Requests_sec_Comparison.png)

![Average Latency Comparison](charts/Average_Latency_Comparison.png)

![Performance Efficiency](charts/Performance_Efficiency.png)


## 📜 License

This project is licensed under the Apache License 2.0.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0
