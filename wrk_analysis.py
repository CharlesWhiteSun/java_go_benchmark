#!/usr/bin/env python3

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 設定資料夾
LOG_DIR = "./benchmark_log"
CHART_DIR = "./benchmark_charts"
REPORT_DIR = "./benchmark_report"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "wrk_results.log")
REPORT_FILE = os.path.join(REPORT_DIR, "report.html")

# Seaborn 基本樣式
sns.set_theme(style="whitegrid")

def parse_wrk_log(filename):
    results = []
    exec_times = {}  # 存放 Benchmark 執行時間
    wrk_config = {}
    benchmark_name = None

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("==="):
            benchmark_name = line.replace("=", "").strip()
        elif "Running" in line and benchmark_name:
            # 抓取執行時間，例如 "Running 1m test"
            match = re.search(r"Running\s+([\d\.]+[smh])\s+test", line)
            if match:
                exec_times[benchmark_name] = match.group(1)
        elif "threads and" in line and benchmark_name:
            # 抓取 threads 和 connections
            match = re.search(r"(\d+)\s+threads\s+and\s+(\d+)\s+connections", line)
            if match:
                wrk_config[benchmark_name] = {
                    "Threads": int(match.group(1)),
                    "Connections": int(match.group(2))
                }
        elif "Requests/sec:" in line and benchmark_name:
            match = re.findall(r"Requests/sec:\s+([\d\.]+)", line)
            if match:
                req_sec = float(match[0])
                results.append({"Benchmark": benchmark_name, "Metric": "Requests/sec", "Value": req_sec})
        elif "CustomAvgLatency" in line and benchmark_name:
            match = re.findall(r"CustomAvgLatency\s+([\d\.]+)ms", line)
            if match:
                latency = float(match[0])
                results.append({"Benchmark": benchmark_name, "Metric": "Avg Latency (ms)", "Value": latency})

    df = pd.DataFrame(results)
    df = df[df["Benchmark"].notna()]
    return df, exec_times, wrk_config

def save_barplot(df, title, filename, order=None):
    plt.figure(figsize=(10, 6))
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    if order:
        pivot_df = pivot_df.set_index("Benchmark").reindex(order).reset_index()

    # 使用 Benchmark 作為 hue，dodge=False 保證柱狀圖置中
    ax = sns.barplot(x="Benchmark", y="Requests/sec", data=pivot_df, hue="Benchmark",
                     dodge=False, palette="Set2", order=order)
    for idx, row in pivot_df.iterrows():
        plt.text(idx, row["Requests/sec"], f'{row["Requests/sec"]:.0f}', ha="center", va="bottom")
    plt.title("Requests/sec Comparison Histogram")
    plt.ylabel("- Requests/sec -")
    plt.xlabel("- Framework Benchmark -")
    plt.xticks(rotation=0, ha="center")
    if (legend := ax.get_legend()) is not None:
        legend.remove()
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()

def save_latency_comparison(df, filename, order=None):
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    if order:
        pivot_df = pivot_df.set_index("Benchmark").reindex(order).reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x="Benchmark", y="Avg Latency (ms)", data=pivot_df, hue="Benchmark",
                     dodge=False, palette="Set2", order=order)
    for idx, row in pivot_df.iterrows():
        plt.text(idx, row["Avg Latency (ms)"], f'{row["Avg Latency (ms)"]:.2f}', ha="center", va="bottom")
    plt.title("Average Latency Comparison Histogram")
    plt.ylabel("- Avg Latency(ms) -")
    plt.xlabel("- Framework Benchmark -")
    plt.xticks(rotation=0, ha="center")
    if (legend := ax.get_legend()) is not None:
        legend.remove()
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()
    return filename

def save_efficiency_chart(df, filename, order=None):
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    if order:
        pivot_df = pivot_df.set_index("Benchmark").reindex(order).reset_index()

    pivot_df["Efficiency"] = pivot_df["Requests/sec"] / pivot_df["Avg Latency (ms)"]

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x="Benchmark", y="Efficiency", data=pivot_df, hue="Benchmark",
                     dodge=False, palette="Set2", order=order)
    for idx, row in pivot_df.iterrows():
        plt.text(idx, row["Efficiency"], f'{row["Efficiency"]:.2f}', ha="center", va="bottom")
    plt.title("Performance Efficiency Histogram")
    plt.ylabel("- Efficiency -")
    plt.xlabel("- Framework Benchmark -")
    plt.xticks(rotation=0, ha="center")
    if (legend := ax.get_legend()) is not None:
        legend.remove()
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()
    return filename

CHART_TITLES = {
    "benchmark_comparison.png": "Requests/sec Comparison",
    "latency_vs_requests.png": "Average Latency Comparison",
    "efficiency.png": "Performance Efficiency"
}

CHART_DESCRIPTIONS = {
    "benchmark_comparison.png": r"""
        <br>
        \( \displaystyle{ Requests/sec = \frac{Total\ Requests}{Execution\ Time\ (seconds)} } \)
        <br>
        <br>
        <ul style="text-align:left; display:inline-block;">
            <li><strong>Purpose:</strong> Compare request throughput (Requests/sec) across different frameworks.</li>
            <li><strong>Basis:</strong> Requests/sec values from wrk benchmark results.</li>
            <li><strong>Interpretation:</strong> Taller bars mean higher throughput under the same conditions.</li>
        </ul>
    """,
    "latency_vs_requests.png": r"""
        <br>
        \( \displaystyle{ AvgLatency(ms) = \frac{Total\ Request\ Latency}{Number\ of\ Requests} } \)
        <br>
        <br>
        <ul style="text-align:left; display:inline-block;">
            <li><strong>Purpose:</strong> Compare average latency (Avg Latency) of different frameworks.</li>
            <li><strong>Basis:</strong> CustomAvgLatency values (ms) from wrk benchmark results.</li>
            <li><strong>Interpretation:</strong> Shorter bars mean lower latency and better responsiveness.</li>
        </ul>
    """,
    "efficiency.png": r"""
        <br>
        \( \displaystyle{ Efficiency = \frac{Requests/sec}{AvgLatency(ms)} } \)
        <br>
        <br>
        <ul style="text-align:left; display:inline-block;">
            <li><strong>Purpose:</strong> Measure the efficiency of frameworks, combining throughput and latency.</li>
            <li><strong>Basis:</strong> Efficiency = Requests/sec ÷ Avg Latency (ms).</li>
            <li><strong>Interpretation:</strong> Higher values indicate a framework can handle more requests with lower latency.</li>
        </ul>
    """
}


def generate_html_report(df, chart_files, order=None, exec_times=None, wrk_config=None):
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    if order:
        pivot_df = pivot_df.set_index("Benchmark").reindex(order).reset_index()

    summary_df = pd.DataFrame({
        "Metric": range(1, len(pivot_df) + 1),
        "Benchmark": pivot_df["Benchmark"],
        "Execution Time": [exec_times.get(b, "N/A") if exec_times else "N/A" for b in pivot_df["Benchmark"]],
        "Threads": [wrk_config.get(b, {}).get("Threads", "N/A") if wrk_config else "N/A" for b in pivot_df["Benchmark"]],
        "Connections": [wrk_config.get(b, {}).get("Connections", "N/A") if wrk_config else "N/A" for b in pivot_df["Benchmark"]],
        "Avg Latency (ms)": pivot_df.get("Avg Latency (ms)", pd.NA),
        "Requests/sec": pivot_df.get("Requests/sec", pd.NA)
    })

    pivot_html = summary_df.to_html(index=False, float_format=lambda x: f"{x:.2f}")

    summary_description = """
        <ul style="text-align:left; display:inline-block;">
            <li><strong>Avg Latency (ms)</strong>: Average time taken to process a request, in milliseconds. Lower values indicate better responsiveness.</li>
            <li><strong>Requests/sec</strong>: Number of requests handled per second. Higher values indicate better throughput.</li>
        </ul>
    """

    html = f"""
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; }}
                h1, h2 {{ text-align: center; color: #333; }}
                hr {{ border: 1px solid #ddd; margin: 30px 0; }}
                img {{ max-width: 100%; height: auto; margin-bottom: 20px; display: block; margin-left: auto; margin-right: auto; }}
                .chart {{ margin-bottom: 40px; }}
                .chart-title {{ text-align: center; font-weight: bold; font-size: 1.2em; margin-bottom: 5px; }}
                .chart-desc {{ font-size: 0.95em; color: #555; margin-bottom: 20px; text-align: center; }}
                table {{ border-collapse: collapse; margin: 0 auto; width: 80%; margin-bottom: 40px; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
                th {{ background-color: #f4f4f4; }}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" defer></script>
        </head>
        <body>
            <h1>Benchmark Report</h1>
            <hr>

            <h2>Summary</h2>
            {summary_description}
            <br>
            <br>
            {pivot_html}
            <hr>

            {"".join([
                f'<div class="chart-title">{CHART_TITLES.get(file, "")}</div>' +
                f'<div class="chart-desc">{CHART_DESCRIPTIONS.get(file, "")}</div>' +
                f'<div class="chart"><img src="../benchmark_charts/{file}"></div><hr>'
                for file in chart_files
            ])}
        </body>
        </html>
    """

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📄 HTML report generated: {REPORT_FILE}")

if __name__ == "__main__":
    df, exec_times, wrk_config = parse_wrk_log(LOG_FILE)
    if df.empty:
        print("找不到可用的 benchmark 資料，請確認 log/wrk_results.log 是否存在且含有資料。")
        raise SystemExit(1)

    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    if "Requests/sec" in pivot_df.columns:
        pivot_sorted = pivot_df.sort_values(by="Requests/sec", ascending=False)
    else:
        pivot_sorted = pivot_df
    ORDER = list(pivot_sorted["Benchmark"])

    print("Order of benchmarks (by Requests/sec desc):", ORDER)
    print(df)

    save_barplot(df, "Benchmark Requests/sec Comparison", "benchmark_comparison.png", order=ORDER)
    chart_files = [
        "benchmark_comparison.png",
        save_latency_comparison(df, "latency_vs_requests.png", order=ORDER),
        save_efficiency_chart(df, "efficiency.png", order=ORDER)
    ]
    generate_html_report(df, chart_files, order=ORDER, exec_times=exec_times, wrk_config=wrk_config)

    print(f"📊 Charts generated in {CHART_DIR}")
    print(f"📄 Report generated at {REPORT_FILE}")
