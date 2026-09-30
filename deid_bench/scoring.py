"""一個 case 對一套系統輸出的評分。"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .clients import GENERIC_LABEL, MaskResult
from .model import Case

# 自家系統代號型別 → 期望型別的對應(OTHER_IDENTIFYING/REL 視為 OTHER)
_NORMALIZE = {"OTHER_IDENTIFYING": "OTHER", "REL": "OTHER"}


def _is_cjk(v: str) -> bool:
    return all(ord(ch) > 0x2E80 for ch in v)


def _partial_leak(v: str, out: str, label: str) -> bool:
    """人名整體不在輸出,但還看得到一部分:頭兩字或尾兩字仍在,
    或緊貼著遮蔽標籤留下第一個字/最後一個字(例如 `[PII:PERSON]彤`)。"""
    label = f"(?:{label})"
    if len(v) >= 3 and (v[:2] in out or v[-2:] in out):
        return True
    if re.search(label + re.escape(v[-1]), out) and v[:-1] not in out:
        return True
    if re.search(re.escape(v[0]) + label, out) and v[1:] not in out:
        return True
    return False


@dataclass
class CaseScore:
    case_id: str
    suite: str
    system: str
    known_gap: bool
    ok: bool                      # 有正常回應(未回應的 case 不進 recall/keep 分母)
    error: str | None
    latency_ms: int
    mask_total: int
    leaked: list[str]             # 該遮卻整個殘留
    partial: list[str]            # 該遮、整體不在,但姓名的頭兩字或尾兩字仍在
    keep_total: int
    overmasked: list[str]         # 該留卻不見了
    wrong_type: list[list[str]]   # [值, 實際型別, 期望型別](僅支援還原的系統)
    extended: list[list[str]]     # [值, 實際被遮的整段](僅支援還原的系統:遮蔽範圍吃到相鄰字)
    inconsistent: list[str]       # 同一原文對到多個代號(僅支援還原的系統)
    roundtrip_ok: bool | None
    observed_masked: dict[str, bool]
    label_counts: dict[str, int]
    output: str = ""
    note: str = ""

    @property
    def recall_hit(self) -> int:
        return self.mask_total - len(self.leaked)

    @property
    def keep_hit(self) -> int:
        return self.keep_total - len(self.overmasked)

    @property
    def clean(self) -> bool:
        return (self.ok and not self.leaked and not self.partial and not self.overmasked and not self.wrong_type
                and not self.extended and not self.inconsistent and self.roundtrip_ok is not False and not self.error)

    def to_dict(self, keep_output: bool = True) -> dict:
        d = asdict(self)
        if not keep_output:
            d["output"] = ""
        return d


def score(case: Case, r: MaskResult, system: str, label_pattern: str | None = None) -> CaseScore:
    """label_pattern:該系統遮蔽標籤的 regex。沒給時,誘餌題改用「輸出是否與原文不同」判斷誤遮。"""
    out = r.output or ""
    ok = r.status == 200 and not (r.error and not out)
    leaked = [v for v in case.mask if v in out] if ok else []
    partial = []
    if ok:
        for v, t in case.mask.items():
            if t == "P_NAME" and v not in out and len(v) >= 2 and _is_cjk(v) and _partial_leak(v, out, label_pattern or GENERIC_LABEL):
                partial.append(v)
    overmasked = [v for v in case.keep if v not in out] if ok else []
    if ok and case.no_mask:
        if r.label_counts:
            overmasked.append("[任何遮蔽] " + ", ".join(f"{k}×{n}" for k, n in r.label_counts.items()))
        elif label_pattern is None and out.strip() != case.text.strip():
            overmasked.append("[輸出與原文不同]")
    wrong_type: list[list[str]] = []
    inconsistent: list[str] = []
    extended: list[list[str]] = []
    if ok and r.types_by_value:
        for seg in r.types_by_value:
            for v in case.mask:
                if v != seg and v in seg and seg not in case.mask:
                    extended.append([v, seg])
        for v, t in case.mask.items():
            if v in leaked or t == "OTHER":
                continue
            actual = _lookup_type(v, r.types_by_value)
            if actual is not None and _NORMALIZE.get(actual, actual) != t:
                wrong_type.append([v, actual, t])
        # 同一個值(含被吃進相鄰字的片段)對到幾個不同代號
        for v in case.mask:
            toks: set[str] = set()
            for seg, segtoks in r.tokens_by_value.items():
                if v in seg:
                    toks |= segtoks
            if len(toks) > 1:
                inconsistent.append(v)
    observed = {v: (v not in out) for v in case.observe} if ok else {}
    return CaseScore(
        case_id=case.id, suite=case.suite, system=system, known_gap=case.known_gap, ok=ok, error=r.error,
        latency_ms=r.latency_ms, mask_total=len(case.mask) if ok else 0, leaked=leaked, partial=partial,
        keep_total=len(case.keep) if ok else 0, overmasked=overmasked, wrong_type=wrong_type, extended=extended, inconsistent=inconsistent,
        roundtrip_ok=r.roundtrip_ok, observed_masked=observed, label_counts=r.label_counts, output=out, note=case.note,
    )


def _lookup_type(value: str, types_by_value: dict[str, str]) -> str | None:
    if value in types_by_value:
        return types_by_value[value]
    # 系統可能把值切成多段或連同前後文一起遮:找包含該值的最短原文
    hits = [(len(k), t) for k, t in types_by_value.items() if value in k]
    if hits:
        return min(hits)[1]
    # 或值被切成幾段(例如地址切成兩個 ADDR):取覆蓋最多字的那段型別
    parts = [(len(k), t) for k, t in types_by_value.items() if k in value and len(k) >= 2]
    if parts:
        return max(parts)[1]
    return None
