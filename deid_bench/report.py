"""把 results JSON 整理成 Markdown 報告。"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from .suites import SUITES


def _pct(hit: int, total: int) -> str:
    return "—" if total == 0 else f"{hit}/{total} ({hit / total * 100:.0f}%)"


def _snip(s: str, n: int = 90) -> str:
    s = s.replace("\n", "⏎")
    return s if len(s) <= n else s[:n] + "…"


def _restore(meta: dict, sy: str) -> bool:
    """該系統是否支援還原(才有型別/一致性/roundtrip 可看)。舊結果檔沒有這個欄位,沿用舊名 mine 判斷。"""
    return bool(meta["systems"][sy].get("restore", sy == "mine"))


def build(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    meta, scores = data["meta"], data["scores"]
    systems = list(meta["systems"])
    rs = [sy for sy in systems if _restore(meta, sy)]
    by = defaultdict(list)
    for s in scores:
        by[(s["suite"], s["system"])].append(s)
    L = [f"# 去識別化基準報告 {meta['started']}", ""]
    L.append(f"- 系統:{', '.join(systems)};case 數 {meta['case_count']};耗時 {meta.get('elapsed_s')} 秒")
    if meta.get("git"):
        L.append("- 版本:" + ", ".join(f"{k} `{v}`" for k, v in meta["git"].items()))
    for sy in systems:
        info = meta["systems"][sy]
        v = info.get("versions") or info.get("health", {}).get("versions")
        desc = f"`{info['type']}` " if info.get("type") else ""
        if v:
            desc += "回報版本:" + ", ".join(f"{k} `{x}`" for k, x in v.items())
        elif info.get("url"):
            desc += f"`{info['url']}`"
        if desc:
            L.append(f"- {sy}:{desc}")
    L.append("")
    L.append("計分:recall = 該遮的值不再出現於輸出;keep = 該保留的值仍在輸出;partial = 人名頭兩字或尾兩字殘留;"
             "type = 代號型別與期望不符(僅支援還原的系統);known gap 另計。")
    L += ["", "## 各套件總覽", ""]
    hdr = "| 套件 | cases |" + "".join(f" {s} recall | {s} keep | {s} partial | {s} p50 ms |" for s in systems) \
        + "".join(f" {s} type錯 |" for s in rs)
    L.append(hdr)
    L.append("|" + "---|" * (hdr.count("|") - 1))
    tot = defaultdict(lambda: [0, 0, 0, 0, 0])
    for suite in SUITES:
        if not any((suite, s) in by for s in systems):
            continue
        row = f"| {suite} | {len(by[(suite, systems[0])])} |"
        for sy in systems:
            ss = [x for x in by[(suite, sy)] if not x["known_gap"]]
            mt, mh = sum(x["mask_total"] for x in ss), sum(x["mask_total"] - len(x["leaked"]) for x in ss)
            kt, kh = sum(x["keep_total"] for x in ss), sum(x["keep_total"] - len(x["overmasked"]) for x in ss)
            pa = sum(len(x["partial"]) for x in ss)
            lat = [x["latency_ms"] for x in ss if x["ok"]]
            p50 = int(statistics.median(lat)) if lat else 0
            row += f" {_pct(mh, mt)} | {_pct(kh, kt)} | {pa} | {p50} |"
            t = tot[sy]
            t[0] += mt; t[1] += mh; t[2] += kt; t[3] += kh; t[4] += pa
        for sy in rs:
            row += f" {sum(len(x['wrong_type']) for x in by[(suite, sy)] if not x['known_gap'])} |"
        L.append(row)
    row = f"| **合計** | {meta['case_count']} |"
    for sy in systems:
        t = tot[sy]
        row += f" **{_pct(t[1], t[0])}** | **{_pct(t[3], t[2])}** | {t[4]} | |"
    for sy in rs:
        row += f" {sum(len(x['wrong_type']) for x in scores if x['system'] == sy and not x['known_gap'])} |"
    L.append(row)

    # 錯誤
    errs = [s for s in scores if not s["ok"]]
    soft = [s for s in scores if s["ok"] and s["error"]]
    if errs or soft:
        L += ["", f"## 請求失敗 / 附帶錯誤(失敗的 case 不進 recall 分母):{len(errs)} / {len(soft)}", ""]
        for s in errs:
            L.append(f"- 失敗 `{s['system']}` {s['case_id']}: {s.get('latency_ms')}ms {s['error']}")
        for s in soft:
            L.append(f"- 有輸出但附帶錯誤 `{s['system']}` {s['case_id']}: {s['error']}")

    for sy in systems:
        L += ["", f"## {sy} 需要看的地方", ""]
        ss = [s for s in scores if s["system"] == sy and s["ok"] and not s["known_gap"]]
        sections = [
            ("漏遮(整個值殘留)", [(s, v) for s in ss for v in s["leaked"]]),
            ("部分殘留(人名頭尾兩字)", [(s, v) for s in ss for v in s["partial"]]),
            ("誤遮(該保留卻消失)", [(s, v) for s in ss for v in s["overmasked"]]),
        ]
        if sy in rs:
            sections.append(("型別錯誤(值 → 實際/期望)", [(s, f"{w[0]} → {w[1]}/{w[2]}") for s in ss for w in s["wrong_type"]]))
            sections.append(("遮蔽範圍吃到相鄰字(值 → 實際被遮整段)", [(s, f"{w[0]} → {w[1]}") for s in ss for w in s["extended"]]))
            sections.append(("同一原文對到多個代號", [(s, v) for s in ss for v in s["inconsistent"]]))
            sections.append(("還原後不等於原文", [(s, "roundtrip") for s in ss if s["roundtrip_ok"] is False]))
        for name, items in sections:
            L.append(f"### {name}:{len(items)}")
            if not items:
                L.append("(無)")
                L.append("")
                continue
            short = [(s, v) for s, v in items if s["suite"] != "longtext"]
            long_ = [(s, v) for s, v in items if s["suite"] == "longtext"]
            if len(short) > 60:
                L.append(f"(短 case 只列前 60 筆,共 {len(short)})")
                short = short[:60]
            for s, v in short:
                L.append(f"- {s['case_id']}: `{v}`  → 輸出:`{_snip(s['output'])}`")
            by_case: dict[str, list[str]] = defaultdict(list)
            for s, v in long_:
                by_case[s["case_id"]].append(v)
            for cid, vals in by_case.items():
                L.append(f"- {cid}: {len(vals)} 個,例如 `{vals[:6]}`")
            L.append("")

    # 所有系統都漏
    if len(systems) >= 2:
        both = []
        per_case: dict[str, dict[str, dict]] = defaultdict(dict)
        for s in scores:
            if s["ok"] and not s["known_gap"]:
                per_case[s["case_id"]][s["system"]] = s
        for cid, d in per_case.items():
            if len(d) == len(systems):
                common = set.intersection(*(set(x["leaked"]) for x in d.values()))
                both += [(cid, v) for v in sorted(common)]
        L += ["", f"## 所有系統都漏(共同盲區):{len(both)}", ""]
        L += [f"- {cid}: `{v}`" for cid, v in both[:80]] or ["(無)"]

    # 觀察項
    obs = defaultdict(dict)
    notes = {}
    for s in scores:
        for v, masked in s["observed_masked"].items():
            obs[(s["case_id"], v)][s["system"]] = masked
            notes[(s["case_id"], v)] = s["note"]
    if obs:
        L += ["", "## 觀察項(政策未定,不計分):值 → 各系統有沒有遮", ""]
        L.append("| case | 值 |" + "".join(f" {s} |" for s in systems) + " 備註 |")
        L.append("|---|---|" + "---|" * len(systems) + "---|")
        for (cid, v), d in obs.items():
            L.append(f"| {cid} | `{_snip(v, 40)}` |" + "".join(f" {'遮' if d.get(s) else '留' if s in d else '?'} |" for s in systems) + f" {notes[(cid, v)]} |")

    # known gap
    kg = [s for s in scores if s["known_gap"]]
    if kg:
        L += ["", "## 已知極限(不計分)", ""]
        for s in kg:
            L.append(f"- `{s['system']}` {s['case_id']}: {s['note']};觀察 {s['observed_masked']}")

    # 長文
    lt = [s for s in scores if s["suite"] == "longtext"]
    if lt:
        L += ["", "## 超長文", ""]
        L.append("| case | 系統 | 個資值 | 漏遮 | 誤遮 | 秒 |")
        L.append("|---|---|---|---|---|---|")
        for s in lt:
            L.append(f"| {s['case_id']} | {s['system']} | {s['mask_total']} | {len(s['leaked'])} | {len(s['overmasked'])} | {s['latency_ms'] / 1000:.1f} |")
        L.append("")
        L.append("漏遮依型別(依 case 期望型別統計):")
        for s in lt:
            if s["leaked"]:
                L.append(f"- {s['system']} {s['case_id']}: 前 15 個 `{s['leaked'][:15]}`")
    L += ["", "## 各系統標籤用量", ""]
    for sy in systems:
        agg = defaultdict(int)
        for s in scores:
            if s["system"] == sy:
                for k, v in s["label_counts"].items():
                    agg[k] += v
        L.append(f"- {sy}: " + ", ".join(f"{k} {v}" for k, v in sorted(agg.items(), key=lambda x: -x[1])))
    return "\n".join(L) + "\n"


def write(path: Path) -> Path:
    md = build(path)
    out = path.with_suffix(".md")
    out.write_text(md, encoding="utf-8")
    return out
