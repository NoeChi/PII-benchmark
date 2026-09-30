"""測試套件登錄表。每個模組提供 cases() -> list[Case]。"""
from __future__ import annotations

from importlib import import_module

from ..model import Case
from .. import pool

SUITES: dict[str, str] = {
    "names_zh": "中文人名:常見、二字、複姓、罕用字、日式、稱謂與相鄰情境",
    "names_foreign": "英文名、羅馬拼音名、中英混排",
    "ids": "身分證、病歷號(有/無關鍵字)、健保卡號、員編/床號等不該遮的號碼",
    "contacts": "電話各種寫法、email 各種寫法、分機",
    "addresses": "完整地址、部分地址、機構名(不該遮)",
    "formats": "同 6 名塞進 30+ 種文字格式(JSON/表格/HTML/YAML…)",
    "structures": "混合個資的密集表格、名冊、班表",
    "scenarios": "擬真臨床文件:入院、出院、交班、會診、社工、雙語",
    "adversarial": "完全沒有個資、但充滿誘餌的文字(量誤遮)",
    "encoding": "全形、零寬字元、換行切斷、URL 編碼、base64",
    "longtext": "合成超長文(多種長度),量時間與逐型別漏遮",
}


def load(name: str, **kw) -> list[Case]:
    mod = import_module(f".{name}", __name__)
    # 每個套件用固定種子,不受載入順序/只跑部分套件影響
    pool.rng.seed(f"{pool.SEED}:{name}")
    cases = mod.cases(**kw) if kw else mod.cases()
    for c in cases:
        c.validate()
    return cases
