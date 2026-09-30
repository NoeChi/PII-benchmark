"""受測系統的 HTTP 客戶端。回傳統一的 MaskResult。

兩種 type:
- http:通用。用 body 範本送出文字,從回應 JSON 的某個欄位取遮蔽結果(任何去識別化 API 都能接)
- deid-web:hermes-stack 的 deid-web,額外用 /api/restore 取回代號↔原文,可量型別/一致性/還原
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class MaskResult:
    output: str = ""
    status: int | None = None
    latency_ms: int = 0
    error: str | None = None
    # 原文 → 系統標的型別(只有支援還原的系統才有;通用 http 留空)
    types_by_value: dict[str, str] = field(default_factory=dict)
    # 原文 → 該值在輸出中用到的代號集合(量一致性)
    tokens_by_value: dict[str, set[str]] = field(default_factory=dict)
    # 還原後是否等於原文
    roundtrip_ok: bool | None = None
    label_counts: dict[str, int] = field(default_factory=dict)


# 沒設定 label_pattern 時用來辨識「遮蔽標籤」的寬鬆樣式(只用於人名部分殘留的判斷)
GENERIC_LABEL = r"\[[^\[\]\n]{1,40}\]|<[A-Z][A-Z_]{1,30}>|\*{2,}|█+"


def _expand_env(v: Any) -> Any:
    """字串裡的 ${VAR} 換成環境變數,方便把 token 放在 .env 而不是設定檔。"""
    if isinstance(v, str):
        return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), v)
    if isinstance(v, dict):
        return {k: _expand_env(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_expand_env(x) for x in v]
    return v


def _fill(template: Any, text: str) -> Any:
    """把 body 範本裡的 "{text}" 換成測資文字(只換值、不動 key)。"""
    if isinstance(template, str):
        return text if template == "{text}" else template.replace("{text}", text)
    if isinstance(template, dict):
        return {k: _fill(v, text) for k, v in template.items()}
    if isinstance(template, list):
        return [_fill(v, text) for v in template]
    return template


def _dig(obj: Any, path: str) -> Any:
    """用 "a.b.0.c" 取巢狀欄位;path 為空字串代表整個回應本身。"""
    if not path:
        return obj
    for part in path.split("."):
        if isinstance(obj, list):
            obj = obj[int(part)]
        elif isinstance(obj, dict):
            if part not in obj:
                raise KeyError(path)
            obj = obj[part]
        else:
            raise KeyError(path)
    return obj


def _count(rx: re.Pattern | None, s: str) -> dict[str, int]:
    out: dict[str, int] = {}
    if rx is None:
        return out
    for m in rx.finditer(s):
        k = next((g for g in m.groups() if g), None) or m.group(0)
        out[k] = out.get(k, 0) + 1
    return out


class HttpClient:
    """通用去識別化 API:POST body 範本 → 從回應取遮蔽後文字。"""

    restore = False

    def __init__(self, name: str, cfg: dict, concurrency: int = 4):
        cfg = _expand_env(cfg)
        self.name = name
        self._url = cfg["url"]
        self._method = cfg.get("method", "POST").upper()
        self._body = cfg.get("body", {"text": "{text}"})
        self._format = cfg.get("format", "json")          # json | form | raw
        self._output = cfg.get("output", "masked")        # 回應 JSON 路徑;response 不是 JSON 時設成 "" 並把 response_type 設 text
        self._response_type = cfg.get("response_type", "json")  # json | text
        self._status_field = cfg.get("status_field")      # 回應裡表示成功與否的欄位(可選)
        self._ok_values = cfg.get("ok_values", ["success", "ok", True])
        self._headers = cfg.get("headers", {})
        pat = cfg.get("label_pattern")
        self.label_pattern = pat
        self._label_rx = re.compile(pat) if pat else None
        self._c = httpx.AsyncClient(timeout=float(cfg.get("timeout", 600)), headers=self._headers,
                                    verify=cfg.get("verify_tls", True))
        self._sem = asyncio.Semaphore(int(cfg.get("concurrency", concurrency)))

    async def start(self) -> dict:
        return {"type": "http", "url": self._url, "label_pattern": self.label_pattern, "restore": False}

    async def close(self) -> None:
        await self._c.aclose()

    async def mask(self, text: str) -> MaskResult:
        body = _fill(self._body, text)
        kw: dict[str, Any] = {}
        if self._format == "json":
            kw["json"] = body
        elif self._format == "form":
            kw["data"] = body
        else:  # raw:body 範本必須是字串
            kw["content"] = body.encode("utf-8") if isinstance(body, str) else json.dumps(body).encode()
        async with self._sem:
            t0 = time.perf_counter()
            try:
                r = await self._c.request(self._method, self._url, **kw)
            except httpx.HTTPError as e:
                return MaskResult(error=f"request failed: {e!r}", latency_ms=int((time.perf_counter() - t0) * 1000))
            ms = int((time.perf_counter() - t0) * 1000)
            if r.status_code != 200:
                return MaskResult(status=r.status_code, latency_ms=ms, error=r.text[:300])
            if self._response_type == "text":
                out, j = r.text, None
            else:
                try:
                    j = r.json()
                    out = _dig(j, self._output)
                except (ValueError, KeyError, IndexError) as e:
                    return MaskResult(status=r.status_code, latency_ms=ms,
                                      error=f"取不到輸出欄位 {self._output!r}: {e!r};回應:{r.text[:200]}")
            if not isinstance(out, str):
                return MaskResult(status=r.status_code, latency_ms=ms, error=f"輸出欄位不是字串:{str(out)[:200]}")
            res = MaskResult(output=out, status=200, latency_ms=ms)
            if self._status_field and j is not None:
                st = _dig(j, self._status_field) if isinstance(j, dict) else None
                if st not in self._ok_values:
                    res.error = f"{self._status_field}={st!r}; response={json.dumps(j, ensure_ascii=False)[:200]}"
            res.label_counts = _count(self._label_rx, out)
            return res


class DeidWebClient:
    """hermes-stack deid-web:/api/deid/text 遮蔽,再用 /api/restore 取回代號↔原文對照。"""

    restore = True
    label_pattern = r"\[([A-Z_]+?)_[0-9a-f]{6}\]"

    def __init__(self, name: str, cfg: dict, concurrency: int = 4):
        cfg = _expand_env(cfg)
        self.name = name
        self._c = httpx.AsyncClient(base_url=cfg["url"], timeout=float(cfg.get("timeout", 900)),
                                    headers=cfg.get("headers", {}))
        self._sem = asyncio.Semaphore(int(cfg.get("concurrency", concurrency)))
        self._rx = re.compile(self.label_pattern)

    async def start(self) -> dict:
        h = (await self._c.get("/healthz")).json()
        await self._c.post("/api/session/new")
        return {"type": "deid-web", "url": str(self._c.base_url), "label_pattern": self.label_pattern,
                "restore": True, "health": h}

    async def close(self) -> None:
        await self._c.aclose()

    async def mask(self, text: str) -> MaskResult:
        async with self._sem:
            t0 = time.perf_counter()
            try:
                r = await self._c.post("/api/deid/text", json={"text": text})
            except httpx.HTTPError as e:
                return MaskResult(error=f"request failed: {e!r}", latency_ms=int((time.perf_counter() - t0) * 1000))
            ms = int((time.perf_counter() - t0) * 1000)
            if r.status_code != 200:
                return MaskResult(status=r.status_code, latency_ms=ms, error=r.text[:300])
            masked = r.json()["masked"]
            res = MaskResult(output=masked, status=200, latency_ms=ms)
            res.label_counts = _count(self._rx, masked)
            try:
                rr = await self._c.post("/api/restore", json={"text": masked})
                if rr.status_code == 200:
                    j = rr.json()
                    res.roundtrip_ok = j["restored"] == text
                    for seg in j["segments"]:
                        if seg.get("token"):
                            m = self._rx.match(seg["token"])
                            res.types_by_value[seg["text"]] = m.group(1) if m else seg["token"]
                            res.tokens_by_value.setdefault(seg["text"], set()).add(seg["token"])
                else:
                    res.error = f"restore HTTP {rr.status_code}: {rr.text[:200]}"
            except httpx.HTTPError as e:
                res.error = f"restore failed: {e!r}"
            return res


TYPES = {"http": HttpClient, "deid-web": DeidWebClient}


def make(name: str, cfg: dict, concurrency: int):
    t = cfg.get("type", "http")
    if t not in TYPES:
        raise SystemExit(f"系統 {name}: 未知 type {t!r}(可用:{', '.join(TYPES)})")
    if "url" not in cfg:
        raise SystemExit(f"系統 {name}: 缺 url")
    return TYPES[t](name, cfg, concurrency)
