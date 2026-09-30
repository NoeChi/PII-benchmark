#!/usr/bin/env bash
# 跑基準:讀 .env 與 systems.toml,打每套受測系統,產報告並與 baseline/latest.json 比較。
# 用法:./run.sh [deid_bench run 的參數…]   例:./run.sh --label after-fix --suites names_zh,ids
set -euo pipefail
cd "$(dirname "$0")"
[[ -f .env ]] && { set -a; source .env; set +a; }
exec uv run python -m deid_bench run "$@"
