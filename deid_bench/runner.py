"""跑所有 case,對每套系統打 API,輸出 results JSON。"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from . import clients as clients_mod
from .model import Case
from .scoring import CaseScore, score
from .suites import SUITES, load


def collect(suites: list[str], long_sizes: tuple[int, ...]) -> list[Case]:
    cases: list[Case] = []
    for s in suites:
        cases += load(s, sizes=long_sizes) if s == "longtext" else load(s)
    ids = [c.id for c in cases]
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"重複的 case id: {dup}"
    return cases


async def run(systems: dict[str, dict], suites: list[str], long_sizes: tuple[int, ...],
              concurrency: int, out_dir: Path, label: str = "") -> Path:
    """systems:系統名 → 設定(見 systems.example.toml)。"""
    cases = collect(suites, long_sizes)
    clients = [clients_mod.make(name, cfg, concurrency) for name, cfg in systems.items()]
    meta = {"started": datetime.now().isoformat(timespec="seconds"), "label": label, "systems": {},
            "suites": suites, "long_sizes": list(long_sizes), "case_count": len(cases)}
    scores: list[CaseScore] = []
    t0 = time.perf_counter()
    done = 0
    try:
        for c in clients:
            meta["systems"][c.name] = await c.start()
        print(f"{len(cases)} cases × {[c.name for c in clients]}", flush=True)
        await _run_all(clients, cases, scores, lambda: done)
    finally:
        await asyncio.gather(*(c.close() for c in clients), return_exceptions=True)
    meta["elapsed_s"] = round(time.perf_counter() - t0, 1)

    return _write(out_dir, label, meta, scores)


async def _run_all(clients, cases, scores, _unused) -> None:
    done = 0

    async def one(client, case: Case):
        nonlocal done
        r = await client.mask(case.text)
        if r.error and not r.output:  # 失敗重試一次
            await asyncio.sleep(2)
            r = await client.mask(case.text)
        s = score(case, r, client.name, client.label_pattern)
        scores.append(s)
        done += 1
        if done % 25 == 0 or "long" in case.tags:
            flag = "clean" if s.clean else f"leak={len(s.leaked)} partial={len(s.partial)} over={len(s.overmasked)} type={len(s.wrong_type)}"
            print(f"  [{done}/{len(cases) * len(clients)}] {client.name:<8} {case.id:<45} {s.latency_ms:>7} ms  {flag}", flush=True)

    # 長文最後跑,避免佔住併發槽
    ordered = sorted(cases, key=lambda c: "long" in c.tags)
    await asyncio.gather(*(one(c, case) for case in ordered for c in clients))


def _write(out_dir: Path, label: str, meta: dict, scores: list[CaseScore]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"{stamp}{('-' + label) if label else ''}.json"
    scores.sort(key=lambda s: (s.suite, s.case_id, s.system))
    payload = {"meta": meta, "scores": [s.to_dict(keep_output=s.suite != "longtext") for s in scores]}
    # 長文輸出另存文字檔,方便肉眼檢查
    for s in scores:
        if s.suite == "longtext" and s.output:
            (out_dir / f"{stamp}-{s.case_id.split('/')[-1]}-{s.system}.txt").write_text(s.output, encoding="utf-8")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def all_suites() -> list[str]:
    return list(SUITES)
