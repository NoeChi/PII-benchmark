#!/usr/bin/env bash
# 給 hermes-stack(GX10)用:起一個隔離的 deid-web 實例(port 8199、獨立 DB)再跑基準,跑完關掉,
# 避免幾百筆測試寫進 production(8100)的 conversion log。
# systems.toml 要有一套 type = "deid-web"、url = "http://127.0.0.1:8199" 的系統。
# 用法:WEB_DIR=~/Taro/Projects/hermes-stack/deid-web scripts/run-with-deid-web.sh [run 參數…]
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f .env ]] && { set -a; source .env; set +a; }
WEB_DIR="${WEB_DIR:?設定 WEB_DIR 指到 deid-web 目錄}"
BENCH_PORT="${BENCH_PORT:-8199}"
URL="http://127.0.0.1:$BENCH_PORT"
mkdir -p results
DB="$(pwd)/results/deid-bench-$(date +%Y%m%d-%H%M%S).db"

web_pid=""
cleanup() { [[ -n "$web_pid" ]] && { kill "$web_pid" 2>/dev/null || true; wait "$web_pid" 2>/dev/null || true; }; }
trap cleanup EXIT INT TERM

if curl -fsS -m 2 "$URL/healthz" >/dev/null 2>&1; then
  echo "port $BENCH_PORT 已有 deid-web 在跑,直接使用"
else
  LOG="$(pwd)/results/deid-web.log"
  ( cd "$WEB_DIR" && set -a && source .env && set +a && DEID_DB_PATH="$DB" PORT="$BENCH_PORT" \
      uv run uvicorn deid_web.main:app --host 127.0.0.1 --port "$BENCH_PORT" >"$LOG" 2>&1 ) &
  web_pid=$!
  for _ in $(seq 1 60); do
    curl -fsS -m 2 "$URL/healthz" >/dev/null 2>&1 && break
    sleep 1
  done
  curl -fsS -m 2 "$URL/healthz" >/dev/null || { echo "deid-web 起不來,見 results/deid-web.log" >&2; exit 1; }
fi
uv run python -m deid_bench run "$@"
