from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import tomllib
from pathlib import Path

from . import baseline, clients, report, runner
from .suites import SUITES, load

ROOT = Path(__file__).resolve().parents[1]


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _add_system_args(r: argparse.ArgumentParser) -> None:
    r.add_argument("--config", default=_env("DEID_BENCH_CONFIG", str(ROOT / "systems.toml")),
                   help="受測系統設定檔(預設 systems.toml;範例見 systems.example.toml)")
    r.add_argument("--systems", default="", help="只跑設定檔裡的這幾套,逗號分隔;預設全部")
    g = r.add_argument_group("臨時指定一套 http 系統(不用設定檔)")
    g.add_argument("--url", help="API 位址;給了就忽略設定檔")
    g.add_argument("--name", default="api", help="系統名稱(報告與基準比較用)")
    g.add_argument("--body", default='{"text": "{text}"}', help='request body 範本(JSON),"{text}" 會換成測資')
    g.add_argument("--output", default="masked", help="回應 JSON 裡遮蔽結果的欄位路徑,例如 data.masked")
    g.add_argument("--header", action="append", default=[], help='額外 header,例如 "Authorization: Bearer xxx";可重複')
    g.add_argument("--label-pattern", default=None, help="遮蔽標籤的 regex,例如 '\\[([A-Z_]+)\\]'")


def _load_systems(a: argparse.Namespace) -> dict[str, dict]:
    if a.url:
        cfg: dict = {"type": "http", "url": a.url, "body": json.loads(a.body), "output": a.output,
                     "headers": dict(h.split(":", 1) for h in a.header)}
        cfg["headers"] = {k.strip(): v.strip() for k, v in cfg["headers"].items()}
        if a.label_pattern:
            cfg["label_pattern"] = a.label_pattern
        return {a.name: cfg}
    path = Path(a.config)
    if not path.exists():
        raise SystemExit(f"找不到設定檔 {path}。複製 systems.example.toml 成 systems.toml 後修改,或用 --url 臨時指定。")
    systems = tomllib.loads(path.read_text(encoding="utf-8")).get("systems", {})
    if a.systems:
        want = [x.strip() for x in a.systems.split(",") if x.strip()]
        missing = [x for x in want if x not in systems]
        if missing:
            raise SystemExit(f"設定檔裡沒有這些系統:{missing}(有:{list(systems)})")
        systems = {k: systems[k] for k in want}
    if not systems:
        raise SystemExit(f"{path} 裡沒有任何 [systems.<名稱>]")
    return systems


async def _check(systems: dict[str, dict]) -> int:
    sample = "病人王小明,身分證 A123456789,電話 0912345678,住台中市西屯區台灣大道四段1650號,由主治醫師看診。"
    bad = 0
    for name, cfg in systems.items():
        c = clients.make(name, cfg, 1)
        try:
            info = await c.start()
            r = await c.mask(sample)
        finally:
            await c.close()
        print(f"===== {name}  {info.get('type')} {info.get('url')}")
        print(f"status={r.status} {r.latency_ms} ms" + (f"  error={r.error}" if r.error else ""))
        print(f"輸入:{sample}\n輸出:{r.output}")
        if r.label_counts:
            print(f"標籤:{r.label_counts}")
        elif info.get("label_pattern"):
            print("⚠ label_pattern 沒有比對到任何標籤,檢查樣式是否正確")
        leaks = [v for v in ("王小明", "A123456789", "0912345678") if v in r.output]
        if r.status != 200 or not r.output:
            bad += 1
            print("✗ 沒拿到輸出")
        else:
            print("✓ 接得上" + (f"(這幾個值沒遮到:{leaks})" if leaks else ""))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="deid_bench")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出所有套件與 case 數")

    ck = sub.add_parser("check", help="送一句範例給每套系統,確認設定接得上")
    _add_system_args(ck)

    r = sub.add_parser("run", help="跑基準,產生 results/<時間>.json 與 .md")
    _add_system_args(r)
    r.add_argument("--suites", default=",".join(SUITES))
    r.add_argument("--long-sizes", default="4000,32000", help="長文字數,逗號分隔;0 = 不跑")
    r.add_argument("--concurrency", type=int, default=int(_env("CONCURRENCY", "4")))
    r.add_argument("--label", default="")
    r.add_argument("--out", default=str(ROOT / "results"))
    r.add_argument("--baseline", default=str(ROOT / "baseline" / "latest.json"), help="跑完自動與此基準比較")

    p = sub.add_parser("report", help="從既有 results JSON 重新產生 Markdown")
    p.add_argument("json")

    c = sub.add_parser("compare", help="比較兩個 results JSON")
    c.add_argument("new")
    c.add_argument("base")

    s = sub.add_parser("baseline", help="把某個 results JSON 設為基準 baseline/latest.json")
    s.add_argument("json")

    d = sub.add_parser("dump", help="印出某套件的所有 case 文字(檢查測資用)")
    d.add_argument("suite")

    a = ap.parse_args()
    if a.cmd == "list":
        total = 0
        for name, desc in SUITES.items():
            n = len(load(name))
            total += n
            print(f"{name:<14} {n:>3}  {desc}")
        print(f"{'total':<14} {total:>3}")
        return 0
    if a.cmd == "dump":
        for c_ in load(a.suite):
            print(f"===== {c_.id}  mask={list(c_.mask)} keep={c_.keep} observe={c_.observe}")
            print(c_.text)
        return 0
    if a.cmd == "check":
        return asyncio.run(_check(_load_systems(a)))
    if a.cmd == "run":
        systems = _load_systems(a)
        sizes = tuple(int(x) for x in a.long_sizes.split(",") if x.strip() and int(x) > 0)
        suites = [x.strip() for x in a.suites.split(",") if x.strip()]
        if not sizes and "longtext" in suites:
            suites.remove("longtext")
        path = asyncio.run(runner.run(
            systems=systems, suites=suites, long_sizes=sizes,
            concurrency=a.concurrency, out_dir=Path(a.out), label=a.label))
        md = report.write(path)
        print(f"\n結果:{path}\n報告:{md}")
        _print_summary(md)
        base = Path(a.baseline)
        if base.exists():
            cmp_md, regress = baseline.compare(path, base)
            cmp_path = path.with_name(path.stem + "-vs-baseline.md")
            cmp_path.write_text(cmp_md, encoding="utf-8")
            print(f"基準比較:{cmp_path}")
            print(cmp_md)
            return 1 if regress else 0
        print("(尚無基準;用 `baseline <json>` 設定)")
        return 0
    if a.cmd == "report":
        print(report.write(Path(a.json)))
        return 0
    if a.cmd == "compare":
        md, regress = baseline.compare(Path(a.new), Path(a.base))
        print(md)
        return 1 if regress else 0
    if a.cmd == "baseline":
        src = Path(a.json)
        if not src.exists():
            print(f"找不到 {src}")
            return 1
        md_src = src.with_suffix(".md")
        if not md_src.exists():
            report.write(src)
        dst = ROOT / "baseline" / "latest.json"
        dst.parent.mkdir(exist_ok=True)
        shutil.copy(src, dst)
        shutil.copy(md_src, dst.with_suffix(".md"))
        print(f"基準已設為 {dst}")
        return 0
    return 1


def _print_summary(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    start = text.index("## 各套件總覽")
    end = text.index("\n## ", start + 5)
    print(text[start:end])


if __name__ == "__main__":
    raise SystemExit(main())
