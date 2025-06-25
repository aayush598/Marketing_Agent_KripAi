# mlops.py
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("mlops_logs")
LOG_DIR.mkdir(exist_ok=True)
MODEL_VERSION = "groq-llama3-70b-8192-v1"

class MLOpsLogger:
    def __init__(self):
        self.log_file = LOG_DIR / f"log_{datetime.now().date()}.jsonl"

    def _log(self, event_type: str, data: dict):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "model_version": MODEL_VERSION,
            "data": data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def log_request(self, endpoint: str, payload: dict):
        self._log("request", {"endpoint": endpoint, "payload": payload})

    def log_response(self, endpoint: str, result: dict, latency: float):
        self._log("response", {
            "endpoint": endpoint,
            "latency_sec": latency,
            "result_summary": str(result)[:1000]  # Truncate to avoid huge logs
        })

    def log_error(self, message: str, details: str = ""):
        self._log("error", {"message": message, "details": details})

    def log_cache_hit(self, endpoint: str, summary: str):
        self._log("cache_hit", {"endpoint": endpoint, "summary": summary[:300]})

    def log_recommendation(self, description: str, budget: str, timeline: str, response_time: float, source: str):
        self._log("recommendation", {
            "description": description[:300],
            "budget": budget,
            "timeline": timeline,
            "source": source,
            "latency_sec": response_time
        })
