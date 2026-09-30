"""把新結果和基準比,列出退步/進步。"""
from __future__ import annotations

import json
from pathlib import Path


def _index(path: Path) -> dict[tuple[str, str], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(s["case_id"], s["system"]): s for s in data["scores"]}


def _bad(s: dict) -> set[str]:
    out = {f"leak:{v}" for v in s["leaked"]} | {f"partial:{v}" for v in s["partial"]} | {f"over:{v}" for v in s["overmasked"]}
    out |= {f"type:{w[0]}→{w[1]}/{w[2]}" for w in s["wrong_type"]} | {f"inconsistent:{v}" for v in s["inconsistent"]}
    out |= {f"extended:{w[0]}→{w[1]}" for w in s.get("extended", [])}
    if s["roundtrip_ok"] is False:
        out.add("roundtrip")
    if not s["ok"]:
        out.add("error")
    return out


def compare(new: Path, base: Path) -> tuple[str, bool]:
    """回傳 (markdown, 有沒有退步)。基準有、新結果沒有的 case 也視為退步(可能是套件被漏跑)。
    只比兩邊都有的系統(用系統名對應);只在其中一邊的系統列出但不算退步。"""
    n, b = _index(new), _index(base)
    ns, bs = {k[1] for k in n}, {k[1] for k in b}
    systems = sorted(ns & bs)
    L = [f"# 基準比較", f"- 新:`{new.name}`", f"- 基準:`{base.name}`", ""]
    any_regress = False
    if not systems:
        L.append(f"(兩邊沒有同名的系統可比:新 {sorted(ns)},基準 {sorted(bs)})")
    elif ns ^ bs:
        L.append(f"(只在其中一邊、不比較的系統:{sorted(ns ^ bs)})")
        L.append("")
    for sy in systems:
        regress, improve = [], []
        keys = sorted(k for k in set(n) | set(b) if k[1] == sy)
        if not keys:
            continue
        for k in keys:
            if k not in b:
                continue
            if k not in n:
                continue
            nb, bb = _bad(n[k]), _bad(b[k])
            if nb - bb:
                regress.append((k[0], sorted(nb - bb)))
            if bb - nb:
                improve.append((k[0], sorted(bb - nb)))
        only_new = [k[0] for k in keys if k not in b]
        only_base = [k[0] for k in keys if k not in n]
        any_regress = any_regress or bool(regress) or bool(only_base)
        L += [f"## {sy}", f"- 退步 {len(regress)} 個 case,進步 {len(improve)} 個 case,新增 {len(only_new)},消失 {len(only_base)}", ""]
        if regress:
            L.append("### 退步")
            L += [f"- {cid}: {', '.join(items)}" for cid, items in regress]
            L.append("")
        if improve:
            L.append("### 進步")
            L += [f"- {cid}: {', '.join(items)}" for cid, items in improve]
            L.append("")
        if only_new:
            L.append("### 基準中沒有的新 case:" + ", ".join(only_new[:30]))
            L.append("")
        if only_base:
            L.append("### 基準有、這次沒跑到的 case(視為退步):" + ", ".join(only_base[:30]) + (" …" if len(only_base) > 30 else ""))
            L.append("")
    return "\n".join(L) + "\n", any_regress
