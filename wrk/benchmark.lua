wrk.method = "GET"
wrk.path = "/ping"
wrk.headers["Content-Type"] = "application/json"

function done(summary, latency, requests)
    -- 自訂平均延遲輸出，避免與 wrk 原始 Latency 衝突
    io.write(string.format("CustomAvgLatency    %.2fms\n", latency.mean / 1000))
end