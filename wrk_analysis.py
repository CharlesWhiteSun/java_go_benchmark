import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 設定資料夾
LOG_DIR = "./log"
CHART_DIR = "./charts"
REPORT_DIR = "./report"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "wrk_results.log")
REPORT_FILE = os.path.join(REPORT_DIR, "benchmark_report.html")

def parse_wrk_log(filename):
    results = []
    with open(filename, "r") as f:
        lines = f.readlines()

    benchmark_name = None
    for line in lines:
        if line.startswith("==="):
            benchmark_name = line.strip("= \n")
        elif "Requests/sec:" in line:
            req_sec = float(re.findall(r"Requests/sec:\s+([\d\.]+)", line)[0])
            results.append({"Benchmark": benchmark_name, "Metric": "Requests/sec", "Value": req_sec})
        elif "Latency" in line and "Avg" in line:
            latency = float(re.findall(r"Latency\s+([\d\.]+)ms", line)[0])
            results.append({"Benchmark": benchmark_name, "Metric": "Avg Latency (ms)", "Value": latency})
    return pd.DataFrame(results)

def save_barplot(df, title, filename):
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Benchmark", y="Value", hue="Metric", data=df)
    plt.title(title)
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()

def save_latency_vs_req(df):
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=pivot_df, x="Requests/sec", y="Avg Latency (ms)", hue="Benchmark", s=150)
    for i in range(len(pivot_df)):
        plt.text(pivot_df["Requests/sec"][i], pivot_df["Avg Latency (ms)"][i], pivot_df["Benchmark"][i])
    plt.title("Latency vs Requests/sec")
    plt.xlabel("Requests/sec")
    plt.ylabel("Avg Latency (ms)")
    plt.tight_layout()
    filename = "latency_vs_requests.png"
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()
    return filename

def save_efficiency_chart(df):
    pivot_df = df.pivot(index="Benchmark", columns="Metric", values="Value").reset_index()
    pivot_df["Efficiency"] = pivot_df["Requests/sec"] / pivot_df["Avg Latency (ms)"]
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Benchmark", y="Efficiency", data=pivot_df)
    plt.title("Performance Efficiency (Requests/sec ÷ Latency)")
    plt.ylabel("Efficiency")
    plt.tight_layout()
    filename = "efficiency.png"
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()
    return filename

def generate_html_report(df, chart_files):
    html = f"""
    <html>
    <head>
        <title>Benchmark Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            img {{ max-width: 100%; height: auto; margin-bottom: 20px; }}
            .chart {{ margin-bottom: 40px; }}
            table {{ border-collapse: collapse; width: 60%; margin-bottom: 40px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Benchmark Report</h1>
        <h2>Summary Table</h2>
        {df.pivot(index="Benchmark", columns="Metric", values="Value").to_html()}
        
        <h2>Charts</h2>
        {"".join([f'<div class="chart"><img src="../charts/{file}"></div>' for file in chart_files])}
    </body>
    </html>
    """
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📄 HTML 報告已生成：{REPORT_FILE}")

if __name__ == "__main__":
    df = parse_wrk_log(LOG_FILE)
    print(df)

    save_barplot(df, "Benchmark Requests/sec & Latency", "benchmark_comparison.png")
    chart_files = [
        "benchmark_comparison.png",
        save_latency_vs_req(df),
        save_efficiency_chart(df)
    ]
    generate_html_report(df, chart_files)

    print(f"📊 圖表已生成在 {CHART_DIR} 資料夾中")
    print(f"📄 報告已生成在 {REPORT_FILE}")
