wrk.method = "GET"
wrk.path = "/ping"
wrk.headers["Content-Type"] = "application/json"

function done(summary, latency, requests)
    io.write(string.format("Latency    %.2fms\n", latency.mean))
end